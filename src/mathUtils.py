"""
file    : mathUtils.py
author  : Max von Hippel and Levi Purdy
authored: 4 July 2021
purpose : Mathematical utilities used in other scripts.
"""
import math
import json

from datetime import datetime


allowed_hoz_deviation = 10 # meters
allowed_vertical_deviation = 10 # meters
allowed_time_deviation = 15 # seconds

"""
The purpose of this function is to check if there is any truth data within
a spatio-temporal bubble (1 minute, 10 meters hoz, 10 meters vertical) of the
given radar point.  We can use this as a kind of simple "validity" check for 
radar data, although it is obviously imperfect.

This is Levi: 
I have added settings for allowed deviations, refer to above for values.
"""
def PAC(time, lat, lon, alt, truth):
	
	for truth_point in truth:	
		
		if None == truth_point.stamp     or \
		   None == truth_point.latitude  or \
		   None == truth_point.longitude or \
		   None == truth_point.altitude:

		   print(json.dumps(truth_point.__dict__))

		   return False

		time_diff = (truth_point.stamp - time).total_seconds()
		
		if (time_diff >= allowed_time_deviation):
			continue
		
		distance_meters = distanceKM(truth_point.latitude, 
		                             truth_point.longitude, 
		                             lat, 
		                             lon) * 1000 
		# Changed this from / to * because converting from Km to m
		
		if distance_meters > allowed_hoz_deviation:
			continue
		
		distance_alt = abs(alt - truth_point.altitude)
		
		if (distance_alt > allowed_vertical_deviation):
			continue
		
		return True
	
	return False

def targetBearing(_azimuth, _radar_orientation):
	tmp_bearing = None
	if (_azimuth <= 0):
		tmp_bearing = -1 * _azimuth
	else:
		tmp_bearing = 360 - _azimuth
	return tmp_bearing + _radar_orientation


# https://stackoverflow.com/a/7835325/1586231
def targetPosition(_range, _azimuth, _elevation, receiver):
	(lat1, lon1, alt1, radar_orientation) = receiver
	
	horizontal_distance = _range * math.cos(math.radians(_elevation)) # METERs
	vertical_distance   = _range * math.sin(math.radians(_elevation)) # METERs
	bearing			 = targetBearing(_azimuth, radar_orientation) # DEGREE_ANGLE

	R = 6.371009 * (10 ** 6) + alt1

	bearing_radians = math.radians(bearing)

	lat1 = math.radians(lat1)
	lon1 = math.radians(lon1)
	
	lat2 = math.asin(
		math.sin(lat1) * math.cos(horizontal_distance / R) +
		math.cos(lat1) * math.sin(horizontal_distance / R) * 
			math.cos(bearing_radians))

	lon2 = lon1 + math.atan2(
				math.sin(bearing_radians) * math.sin(horizontal_distance / R) 
					* math.cos(lat1),
			 	math.cos(horizontal_distance / R) - math.sin(lat1) 
			 		* math.sin(lat2))

	lat2 = math.degrees(lat2)
	lon2 = math.degrees(lon2)
	alt2 = alt1 + vertical_distance

	return (lat2, lon2, alt2)

def distanceKM(lat1, lon1, lat2, lon2):
	if (lat1, lon1) == (lat2, lon2):
		return 0
	R = 6373.0 # radius of the Earth in km
	lat1 = math.radians(lat1)
	lon1 = math.radians(lon1)
	lat2 = math.radians(lat2)
	lon2 = math.radians(lon2)
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	
	# Haversine formula
	a = math.sin(dlat / 2) ** 2 \
	  + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2

	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	
	distance = R * c

	return distance