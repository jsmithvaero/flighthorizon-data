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
from src.Point          import Point

class RadarDataGroundAware(Data):

	folder         = None
	points         = None
	radarLocations = None

	# Should fill in the data from the folder
	def fromFolder(self, folder):
		self.folder = folder
		points = {}
		rcvrs  = {}
		for file in glob(folder + "**/*.vlog", recursive=True):
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
		pass

	"""
	Extra Functionality That Extends Data Class
	"""
	def getRADARlocations(self):
		pass

	def quickStats(self):
		ret = "Groundaware Radar Quick Stats: ["
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
	pass


"""
INPUT : radar_file_name - the file name of the RADAR log file to be parsed
OUTPUT: the data from radar_file_name, in the format 
        [ ... (time, conf, lat, lon, alt, dist) ...]
"""
def getRadarPoints(radar_file_name):
	points = []
	with open(radar_file_name, "r") as fr:
		stuff = json.loads(fr.read())
		track = stuff["track"]
		track_id = track["id"]
		for entry in track["updates"]:
			updateTime = entry["update_time"]
			position =  entry["position"] 
			lat = position["latitude"]
			lon =  position["longitude"]
			alt =  position["altitude"]	
			dist = entry["distance"]
			speed = entry["speed"]	
			classification = entry["classification"][0]
			conf = classification["likelihood"];

			p = Point()
			p.updateTime 		= updateTime
			p.confidence 		= conf
			p.latitude 			= lat
			p.longitude 		= lon
			p.altitude 			= alt
			p.distance 			= dist
			p.speed 			= speed
			p.trackID 			= track_id
			points.append(p)

	return points