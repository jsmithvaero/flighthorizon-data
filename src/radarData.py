"""
file    : radarData.py
author  : Max von Hippel
authored: 4 July 2021
purpose : Data handler for RADAR
"""
from Data import Data
from glob import glob
from mathUtils        import targetBearing, targetPosition, distanceKM
from genericDataUtils import getConfigName

class RadarData(Data):

	self.folder         = None
	self.radarLocations = None

	# Should fill in the data from the folder
	def fromFolder(self, folder):
		self.folder = folder
		points = {}
		rcvrs  = {}
		for file in glob(folder + "**/*radar.log", recursive=True):
			subpoints = getRadarPoints(file)
			if subpoints != None:
				subname = getConfigName(file)
				if subname in points:
					points[subname] += subpoints
				else:
					points[subname] = subpoints
		self.points = points 

	# Should return the current format
	def getFormat(self):
		return {
			"name" : [
				"time"       : "datetime",
				"confidence" : "percent",
				"latitude"   : "degree",
				"longitude"  : "degree",
				"altitude"   : "meter",
				"distance"   : "meter"
			]
		}

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
	except:
		print("TODO - deal with these radar files that lack configs")
		return None


"""
INPUT : radar_file_name - the file name of the RADAR log file to be parsed
OUTPUT: the data from radar_file_name, in the format 
        [ ... (time, conf, lat, lon, alt, dist) ...]
"""
def getRadarPoints(radar_file_name):
	receiver = getRadarConfigLocation(radar_file_name)
	if receiver == None:
		print("Not plotting " \
			+ radar_file_name \
			+ ", because we lack the RADAR configuration file.")
		return None
	points = []
	with open(radar_file_name, "r") as fr:
		stuff = json.loads(fr.read())
		for entry in stuff:
			(rn, az, el) = (entry["rest"], entry["azest"], entry["elest"])
			(lat, lon, alt) = calculateTargetPosition(rn, az, el, receiver)
			# print("Passing in: ", lat, lon, receiver[0], receiver[1])
			dist = 1000 * distance_km(lat, lon, receiver[0], receiver[1])
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