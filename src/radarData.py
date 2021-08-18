"""
file    : radarData.py
author  : Max von Hippel
authored: 4 July 2021
purpose : Data handler for RADAR
"""
import json
import math
import pymap3d
import numpy                   as np
import glob
import dateutil.parser
import os
from   scipy.spatial.transform import Rotation
import numpy                   as np
from   collections             import OrderedDict
from   datetime                import datetime
from   datetime                import timedelta
from   src.Data                import Data
from   glob                    import glob
from   src.mathUtils           import targetBearing,  \
                                      targetPosition, \
                                      distanceKM
from   src.genericDataUtils    import getConfigName
from   src.plotGraphs          import *
from   src.Point               import Point
from   src.Physical            import Physical
from   src.FoV                 import FoV
from   src.dateParser          import parseDate

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
			lon   = stuff["receiver"]["longitude"  ]["value"]
			lat   = stuff["receiver"]["latitude"   ]["value"]
			alt   = stuff["receiver"]["elevation"  ]["value"]
			ori   = stuff["receiver"]["orientation"]["value"]
			
			# Check membership instead of equality due to peculiarities of
			# Windows encoding.
			assert("°" in stuff["receiver"]["longitude"  ]["unit"])
			assert("°" in stuff["receiver"]["latitude"   ]["unit"])
			assert("m" in stuff["receiver"]["elevation"  ]["unit"])
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
	try:
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
				time = parseDate(entry["timeStamp"])
				
				conf = entry["confidenceLevel"]
				trackID = entry["id"]
				
				p                  = Point()
				p.stamp            = time
				p.confidence       = conf
				p.latitude         = lat
				p.longitude        = lon
				p.altitude         = alt
				p.distance         = dist
				p.verticalVelocity = velVert
				p.xVelocity        = velX
				p.yVelocity        = velY
				p.azimuth          = az
				p.elevation        = el
				p.range            = rn
				p.src              = radar_file_name
				p.trackID 		   = trackID
				points.append(p)
	except Exception as e:
		return []
	return points
"""
Function to find the first timestamp in a _radar.log file.
This is here because the filename uses 12 hr format, but does not specify AM or
PM, so the point in the file with a valid timestamp should be used instead.

Adapted code from getRadarPoints
"""
def get_first_timestamp_in_radarLog(radar_file_name):
	with open(radar_file_name, "r") as fr:
		stuff = json.loads(fr.read())
		for entry in stuff:
			time = parseDate(entry["timeStamp"])
			return time
"""
Find radar config file. Given a radar Point will find the closest timestamped 
echogarud RadarConfig file and return the name.

Sources:
	https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-
	directory

	https://stackoverflow.com/questions/12141150/from-list-of-integers-get-
	number-closest-to-a-given-value

Notes:
	RadarConfig_time_zone should be made to use datetime timezone info 
	eventually

	use_filename_date off by default
"""
def find_RadarConfig(
	radar_point, 
	RadarConfig_time_zone=timedelta(hours=-9), 
	use_filename_date=False):
	
	radar_log_file = ('..\\' + radar_point.src)    \
		if 'src' in os.path.dirname(__file__) else \
		radar_point.src

	# Parse datetime out of the radar_log_file
	if use_filename_date:
	
		radar_log_filename = os.path.basename(radar_log_file)
		radar_log_datestring = radar_log_filename.split('_')[0]
		log_date = dateutil.parser.isoparse(radar_log_datestring)
	
	else:
	
		log_date = get_first_timestamp_in_radarLog(radar_log_file)

	# Get list of RadarConfig files
	echoguard_folder = os.path.join(os.path.dirname(radar_log_file), 
		                            'echoguard')
	
	echoguard_folder = ('..\\' + echoguard_folder) \
				if 'src' in os.path.dirname(__file__) else \
				echoguard_folder
	radar_filenames = next(os.walk(echoguard_folder), (None, None, []))[2]

	date_list = {}

	# Parse into a list of datetimes
	for config_name in radar_filenames:
		
		if 'RadarConfig' in config_name:
		
			date_string = config_name.split('_')[1].split('.')[0]
			
			date = dateutil.parser.isoparse(date_string) - RadarConfig_time_zone
			
			date_list.update({date: config_name})

	# Find the closest *maybe prior* datetime and return the RadarConfig paths
	closest_date = min(date_list, key=lambda date: abs(date - log_date))
	radar_config_file = date_list.get(closest_date)

	return os.join(echoguard_folder, radar_config_file)

"""
Grabs data from a echoguard RadarConfig file. 

Returns a physical object with a fov object inside 
"""
def parse_RadarConfig(radar_RadarConfig_file):

	pass


# This function will be here for future implementations when a radar 
# logfile can contain the orientation information
# For now it will just return a generic radar fov for Echodyne GroundAware
# radars. TODO: get_radar_fov needs a link into parse_RadarConfig
def get_radar_fov(radar_log_file):

	fov = FoV()

	# RadarConfigFile = find_RadarConfig(radar_log_file)

	fov.range     = 5000
	fov.rangeUnit = "meter"
	fov.AzMin     = -60
	fov.AzMinUnit = "degree"
	fov.AzMax     = 60
	fov.AzMaxUnit = "degree"
	fov.ElMin     = -40
	fov.ElMinUnit = "degree"
	fov.ElMax     = 40
	fov.ElMaxUnit = "degree"

	# Fill out the rest here
	return fov

# TODO: get_radar_physical needs a link into parse_RadarConfig
def get_radar_physical(radar_log_file):
	
	physical = Physical()

	lat, lon, alt, ori = getRadarConfigLocation(radar_log_file)

	physical.lat     = lat
	physical.lon     = lon
	physical.alt     = alt
	physical.heading = ori

	physical.latUnit     = "degree"
	physical.lonUnit     = "degree"
	physical.altUnit     = "meter"
	physical.headingUnit = "degree"

	# Temporary values for Testing, should be replaced with some refrence system
	# to RadarConfig_*.json stuff

	physical.pitch = 0
	physical.roll  = 0

	physical.pitchUnit = "degree"
	physical.pitchUnit = "degree"

	return physical


# Tests if testTruth is in the FoV of a radar described by a range
# Unless a breakpoint is set before plot_vectors(vectors, ax) 
# generate_debug_graph will freeze the execution
def is_point_in_fov(
	RD_point,
	TD_point,
	useRadarAsCenter=True, 
	useRangeAsTrue=False,
	calculate_Az_El_when_out_of_range=True, 
	generate_debug_graph=False,
	fov = None,
	physical = None,
	centerLat=0, 
	centerLon=0, 
	centerAlt=0):

	# (datetime.datetime(2021, 1, 27, 20, 3, 20, 88000), 
	# 0.0, 65.12624067, -147.47648183, 211.8, 0, 0.0, 0.0, 0.0, 
	# 0.0, 0.0, 0.0, 'demo-data/2021.january.27\\20210127T080320_radar.log')

	# Setup variables

	if not fov or not physical:
		fov      = get_radar_fov     (RD_point.src)
		physical = get_radar_physical(RD_point.src)
	
	return_object = Point()

	truthTime, truthLat, truthLon, truthAlt = TD_point.stamp,     \
	                                          TD_point.latitude,  \
	                                          TD_point.longitude, \
	                                          TD_point.altitude
	
	# Using the radar's location as 0,0,0 (optional) in enu coordinates
	# e:East n:North u:Up
	
	if useRadarAsCenter:
	
		centerLat = physical.lat
		centerLon = physical.lon
		centerAlt = physical.alt

	if useRangeAsTrue:
	
		truthLat = RD_point.latitude
		truthLon = RD_point.longitude
		truthAlt = RD_point.altitude

	# translate the plane's lat, lon, alt into enu
	e, n, u = pymap3d.geodetic2enu(truthLat, 
								truthLon,
								truthAlt,
								centerLat,
								centerLon,
								centerAlt,
								deg=True)
	
	plane_position = np.array([e, n, u])

	# translate the radar's location into enu, usually this will be 0,0,0 unless 
	# custom center is used
	e, n, u = pymap3d.geodetic2enu(physical.lat, 
								   physical.lon,
								   physical.alt,
								   centerLat,
								   centerLon,
								   centerAlt,
								   deg=True)
	
	radar_position = np.array([e, n, u])

	# (v1 = plane_position-radar_position)
	v1 = plane_position-radar_position

	# Calculate distance between the radar and the plane
	distance = np.linalg.norm(v1)
	return_object.range = distance
	if distance < fov.range:
		return_object.is_in_range = True
	else:
		return_object.is_in_range = False
		return_object.is_in_fov = False

	if return_object.is_in_range or calculate_Az_El_when_out_of_range:

		# Make a quaternion describing the rotation of the radar
		# this is an extrinsic rotation, not intrinsic, so capital letters
		# remember e, n, u coordinate system, x, y, z
		
		radar_orientation = Rotation.from_euler('ZXY', 
			                                    [-physical.heading, 
			                                      physical.pitch, 
			                                      physical.roll
			                                    ], 
			                                    degrees=True)

		# Create a vector that is just [fov.range, 0,0] and then rotate its 
		# reference frame by the radar orientation quaternion
		
		radar_range_base_vector = np.array([0, fov.range, 0])
		
		# This creates v2 (the center fov vector of the radar)
		radar_FoV_center_vector \
			= radar_orientation.apply(radar_range_base_vector)
		
		v2 = radar_FoV_center_vector
		
		# Maybe rotate vector v1 by the frame of the radar's rotation
		# Yes I am choosing to add this, because if the v1 vector is rotated 
		# about the v2 vector by -physical.roll,
		# it will allow planer x, y tests to work for angle ranges
		
		roll_radians = np.radians(-physical.roll)
		
		radar_FoV_center_vector_norm \
			= radar_FoV_center_vector / np.linalg.norm(radar_FoV_center_vector)
		
		radar_roll_rot \
			= Rotation.from_rotvec(radar_FoV_center_vector_norm * roll_radians)
		
		v1_rot = radar_roll_rot.apply(v1)

		if generate_debug_graph:
			
			# Setup some optional test plots to check and make sure the vectors 
			# are working correctly
			# https://stackoverflow.com/questions/27023068/plotting-3d-vectors-
			# using-python-matplotlib
			
			ax = plot_vector_setup()
			u_1, v_1, w_1 = v1
			u_2, v_2, w_2 = v2
			x, y, z = radar_position
			vectors = np.array([[x, y, z, u_1, v_1, w_1], \
				                [x, y, z, u_2, v_2, w_2]])
			
			plot_radar_fov_indicators(radar_position, fov, physical, ax)
			plot_vectors(vectors, ax)
			plt.show()


		# Normalize the vectors
		norm_v1_rot = v1_rot / np.linalg.norm(v1_rot)
		norm_v2     = v2     / np.linalg.norm(v2    )

		# Find the angle between v1 and v2 vectors
		v1_rot_xy = [norm_v1_rot[0], norm_v1_rot[1], 0]
		v2_rot_xy = [norm_v2[0]    , norm_v2[1]    , 0]
		
		x1, y1 = np.linalg.norm(np.cross(v1_rot_xy, v2_rot_xy)), \
		                        np.dot  (v1_rot_xy, v2_rot_xy)
		
		relative_heading_angle   = np.degrees(np.arctan2(x1, y1))
		
		relative_elevation_angle = np.degrees(np.arcsin(norm_v1_rot[2] - \
			                                            norm_v2[2]))

		# Compare the angle between them and check if they are out of range

		return_object.relative_heading   = relative_heading_angle
		return_object.relative_elevation = relative_elevation_angle

		return_object.is_in_heading \
			= (relative_heading_angle > fov.AzMin and \
			   relative_heading_angle < fov.AzMax)

		return_object.is_in_elevation \
			= (relative_elevation_angle > fov.ElMin and \
			   relative_elevation_angle < fov.ElMax)

		return_object.is_in_fov \
			= (return_object.is_in_range   and \
		       return_object.is_in_heading and \
		       return_object.is_in_elevation)

		return return_object
	else:
		return return_object
