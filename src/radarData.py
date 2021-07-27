"""
file    : radarData.py
author  : Max von Hippel
authored: 4 July 2021
purpose : Data handler for RADAR
"""
import json
import math
import pymap3d
import numpy as np
from scipy.spatial.transform import Rotation

from collections import OrderedDict
from datetime    import datetime

from src.Data import Data
from glob import glob
from src.mathUtils        import targetBearing, targetPosition, distanceKM
from src.genericDataUtils import getConfigName
from src.plotGraphs import *

class RadarData(Data):

	folder         = None
	points         = None
	radarLocations = None

	# Should fill in the data from the folder
	def fromFolder(self, folder):
		self.folder = folder
		points = {}
		rcvrs  = {}
		for file in glob(folder + "**/*radar.log", recursive=True):
			subpoints = getRadarPoints(file)
			if subpoints != None:
				subname = getConfigName(file)
				if subname == None:
					subname = file.split("/")[-1].split(".")[0].strip()
				if subname in points:
					points[subname] += subpoints
				else:
					points[subname] = subpoints
		self.points = points 

	# Should return the current format
	def getFormat(self):
		ret         = OrderedDict()
		ret["name"] = OrderedDict()
		ret["name"]["time"            ] = "datetime"
		ret["name"]["confidence"      ] = "percent"
		ret["name"]["latitude"        ] = "degree"
		ret["name"]["longitude"       ] = "degree"
		ret["name"]["altitude"        ] = "meter"
		ret["name"]["distance"        ] = "meter"
		ret["name"]["verticalVelocity"] = "meter/second"
		ret["name"]["xVelocity"       ] = "meter/second"
		ret["name"]["yVelocity"       ] = "meter/second"
		ret["name"]["azimuth"] = "degree"
		ret["name"]["elevation"] = "degree"
		ret["name"]["range"] = "meter"
		ret["name"]["source"] = "filename"
		return ret

	"""
	Extra Functionality That Extends Data Class
	"""
	def getRADARlocations(self):
		folder = self.folder
		assert(folder != None)
		if self.radarLocations != None:
			return self.radarLocations
		rcvrs = []
		for file in glob(folder + "**/*radar.log", recursive=True):
			conf_rcvr = getRadarConfigLocation(file)
			if conf_rcvr != None:
				lat, lon, alt, ori = conf_rcvr
				rcvr = { "lat": lat, "lon": lon, "alt": alt }
				rcvrs.append(rcvr)
		self.radarLocations = rcvrs
		return self.radarLocations

	def quickStats(self):
		ret = "Radar Quick Stats: ["
		if self.folder == None:
			ret += " no folder. ]"
			return ret
		for name in self.points:
			num_points = len(self.points[name])
			ret += "\n\t" + str(name) + " - " + str(num_points) + " points"
		return ret + "\n]"

"""
-------------------- RADAR UTILITY FUNCTIONS PROVIDED BELOW --------------------
"""


"""
INPUT : radar_file_name - the file name of the RADAR log file to be parsed
OUTPUT: the location (lat,    lon,    alt,   ori   ) in units of 
                     (degree, degree, meter, degree)
        of the RADAR, if we can determine it; else None
"""
def getRadarConfigLocation(radar_file_name):
	radar_config_file_name = radar_file_name.replace(".log", "_config.log")
	lat, lon, alt, ori = None, None, None, None
	try:
		with open(radar_config_file_name, "r") as fr:
			stuff = json.loads(fr.read())
			lon = stuff["receiver"]["longitude"]["value"]
			lat = stuff["receiver"]["latitude"]["value"]
			alt = stuff["receiver"]["elevation"]["value"]
			ori = stuff["receiver"]["orientation"]["value"]
			# == changed to in because running environment was adding a random special character
			assert("°" in stuff["receiver"]["longitude"]["unit"])
			assert("°" in stuff["receiver"]["latitude"]["unit"])
			assert("m" in stuff["receiver"]["elevation"]["unit"])
			assert("°" in stuff["receiver"]["orientation"]["unit"])
		return lat, lon, alt, ori
	except Exception as e:
		return None


"""
INPUT : radar_file_name - the file name of the RADAR log file to be parsed
OUTPUT: the data from radar_file_name, in the format 
        [ ... (time, conf, lat, lon, alt, dist) ...]
"""
def getRadarPoints(radar_file_name):
	receiver = getRadarConfigLocation(radar_file_name)
	if receiver == None:
		return None
	points = []
	with open(radar_file_name, "r") as fr:
		stuff = json.loads(fr.read())
		for entry in stuff:
			(rn, az, el) = (entry["rest"], entry["azest"], entry["elest"])
			
			(velVert, velX, velY) = (entry["velzest"], 
				                     entry["velxest"], 
				                     entry["velyest"])

			(lat, lon, alt) = targetPosition(rn, az, el, receiver)
			# print("Passing in: ", lat, lon, receiver[0], receiver[1])
			dist = 1000 * distanceKM(lat, lon, receiver[0], receiver[1])
			time = None
			try:
				time = datetime.strptime(entry["timeStamp"], \
										 "%Y-%m-%dT%H:%M:%S.%fZ")
			except:
				time = datetime.strptime(entry["timeStamp"], \
										 "%Y-%m-%dT%H:%M:%SZ")
			conf = entry["confidenceLevel"]
			points.append((time,
				           conf, 
				           lat, 
				           lon, 
				           alt, 
				           dist, 
				           velVert, 
				           velX, 
				           velY,
						   az,
						   el,
						   rn,
						   radar_file_name))
	return points

# This is just a placeholder object that can have attributes added to it. Used for quick construction of passable objects
class Object(object):
    pass


# This function will be here for future implementations when a radar logfile can contain the orientation information
# For now it will just return a generic radar fov for Echodyne GroundAware radars.
def get_radar_fov(radar_log_file):

	fov = Object()
	fov.range = 5000
	fov.rangeUnit = "meter"
	fov.AzMin = -60
	fov.AzMinUnit = "degree"
	fov.AzMax = 60
	fov.AzMaxUnit = "degree"
	fov.ElMin = -40
	fov.ElMinUnit = "degree"
	fov.ElMax = 40
	fov.ElMaxUnit = "degree"

	# Fill out the rest here
	return fov


def get_radar_physical(radar_log_file):
	physical = Object()

	if 'src' in os.path.dirname(__file__):
		lat, lon, alt, ori = getRadarConfigLocation('..\\' + radar_log_file)
	else:
		lat, lon, alt, ori = getRadarConfigLocation(radar_log_file)

	physical.lat = lat
	physical.lon = lon
	physical.alt = alt
	physical.heading = ori

	physical.latUnit = "degree"
	physical.lonUnit = "degree"
	physical.altUnit = "meter"
	physical.headingUnit = "degree"

	# Temporary values for Testing, should be replaced with some refrence system to RadarConfig_*.json stuff
	physical.pitch = 15
	physical.roll = 0

	physical.pitchUnit = "degree"
	physical.pitchUnit = "degree"

	return physical


# Tests if testTruth is in the FoV of a radar described by a range
def is_point_in_fov(range, testTruth, useRadarAsCenter=True, centerLat=0, centerLon=0, centerAlt=0):
	# (datetime.datetime(2021, 1, 27, 20, 3, 20, 88000), 0.0, 65.12624067, -147.47648183, 211.8, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'demo-data/2021.january.27\\20210127T080320_radar.log')

	# Setup variables
	time, conf, lat, lon, alt, dist, velVert, velX, velY, az, el, rn, radar_log_file = range
	fov = get_radar_fov(radar_log_file)
	physical = get_radar_physical(radar_log_file)

	truthTime, truthLat, truthLon, truthAlt = testTruth
	# Using the radar's location as 0,0,0 (optional) in enu coordinates translate the plane's lat, lon, alt into enu
	# e:East n:North u:Up
	if useRadarAsCenter:
		centerLat = lat
		centerLon = lon
		centerAlt = alt

	e, n, u = pymap3d.geodetic2enu(truthLat, truthLon, truthAlt, centerLat, centerLon, centerAlt, deg=True)
	plane_position = np.array([e, n, u])
	e, n, u = pymap3d.geodetic2enu(lat, lon, alt, centerLat, centerLon, centerAlt, deg=True)
	radar_position = np.array([e, n, u])

	# (v1 = plane_position-radar_position)
	v1 = plane_position-radar_position

	# Make a quaternion describing the rotation of the radar

	# in roll pitch yaw x, y, z
	# z Yaw
	# y Pitch
	# x Roll

	# z Yaw
	# Y Pitch
	# x Roll

	# z, y, x (roll pitch yaw) seems to be common
	# z roll
	# y pitch
	# x yaw

	# Another random image
	# z Roll
	# y yaw
	# x pitch

	# Ok, so e n u is x y z so if facing north is 0 0 0: heading is z/e, roll is y/n, pitch is z/u
	# z heading
	# y roll
	# x pitch

	radar_orientation = Rotation.from_euler('ZYX',[-physical.heading, physical.roll, physical.pitch], degrees=True)

	# Create a vector that is just [fov.range, 0,0] and then rotate its reference frame by the radar orientation quaternion
	radar_range_base_vector = np.array([0, fov.range, 0])
	# This creates v2 (the center fov vector of the radar)
	radar_FoV_center_vector = radar_orientation.apply(radar_range_base_vector)
	v2 = radar_FoV_center_vector
	#
	# Maybe rotate vector v1 by the frame of the radar's rotation
	#
	# Setup some optional test plots to check and make sure the vectors are working correctly
	# https://stackoverflow.com/questions/27023068/plotting-3d-vectors-using-python-matplotlib
	ax = plot_vector_setup()
	u1, v1, w1 = v1
	u2, v2, w2 = v2
	x, y, z = radar_position
	vectors = np.array([[x,y,z, u1, v1, w1],[x,y,z, u2, v2, w2]])
	plot_radar_fov_indicators(radar_position, fov, physical, ax)
	plot_vectors(vectors, ax)


	# Find the angle between v1 and v2 vectors
	# Normalize the vectors
	# Compare the angle between them and check if they are out of range

	return