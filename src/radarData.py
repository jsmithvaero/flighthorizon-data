"""
file    : radarData.py
author  : Max von Hippel
authored: 4 July 2021
purpose : Data handler for RADAR
"""
import json
import math

from collections import OrderedDict
from datetime    import datetime

from src.Data import Data
from glob import glob
from src.mathUtils        import targetBearing, targetPosition, distanceKM
from src.genericDataUtils import getConfigName

class RadarData(Data):

	folder         = None
	points         = None
	radarLocations = None

	def __init__(self, folder):
		self.fromFolder(folder)

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
		ret["name"]["time"      ] = "datetime"
		ret["name"]["confidence"] = "percent"
		ret["name"]["latitude"  ] = "degree"
		ret["name"]["longitude" ] = "degree"
		ret["name"]["latitude"  ] = "meter"
		ret["name"]["distance"  ] = "meter"
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
			assert("°" == stuff["receiver"]["longitude"]["unit"])
			assert("°" == stuff["receiver"]["latitude"]["unit"])
			assert("m" == stuff["receiver"]["elevation"]["unit"])
			assert("°" == stuff["receiver"]["orientation"]["unit"])
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
			points.append((time, conf, lat, lon, alt, dist))
	return points