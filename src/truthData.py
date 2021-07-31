from collections import OrderedDict
from glob        import glob
from datetime    import datetime

import json

from src.Data  import Data
from src.Point import Point

class TruthData(Data):

	def quickStats(self):
		return "Truth Data Quick Stats : [ " \
		       + str(len(self.points)) + " points ]"

	# EXTRA FUNCTIONALITY ABOVE DATA CLASS
	def union(self, otherTruth):
				
		new_points = self.points.union(otherTruth.getPoints())

		return TruthData(folder=None, points=new_points)
		
"""
ADSB
"""
class ADSBData(TruthData):

	# Should fill in the data from the folder
	def fromFolder(self, folder):
		points = set()
		for file in glob(folder + "**/*adsb.log", recursive=True):
			points = points.union(set(getADSBpoints(file)))
		self.points = points

	def quickStats(self):
		return "ADSB Quick Stats : [ " + str(len(self.points)) + " points ]"

def getADSBpoints(adsb_file_name):
	points = []
	with open(adsb_file_name, "r") as fr:
		stuff = json.loads(fr.read())
		for entry in stuff:
			(lat, lon, alt) = (entry["latDD"],  \
							   entry["lonDD"], \
							   entry["altitudeMM"])
			alt = float(alt) / 1000 # mm -> m
			time = None
			try:
				time = datetime.strptime(entry["timeStamp"], \
										 "%Y-%m-%dT%H:%M:%S.%fZ")
			except:
				time = datetime.strptime(entry["timeStamp"], \
										 "%Y-%m-%dT%H:%M:%SZ")
			if (lat, lon) != (0.0, 0.0):
				p           = Point()
				p.stamp     = time
				p.latitude  = lat
				p.longitude = lon
				p.altitude  = alt
				points.append(p)
	return points

"""
NMEA
"""
class NMEAData(TruthData):

	# Should fill in the data from the folder
	def fromFolder(self, folder):
		points = set()
		for file in glob(folder + "**/*.nmea", recursive=True):
			if "_" in file:
				year, month, day, _ = ntpath.basename(file).split("_", 3)
				year  = int(year)
				month = int(month)
				day   = int(day)
			points = points.union(getNMEApoints(file, date(year, month, day)))
		self.points = points

	def quickStats(self):
		return "NMEA Quick Stats : [ " + str(len(self.points)) + " points ]"
	

def getNMEApoints(nmea_file_name, date):
	points = set()
	with open(nmea_file_name, "r", encoding='utf-8') as fr:
		for line in fr:
			try:
				p = Point()

				msg  = pynmea2.parse(line)
				
				p.latitude  = msg.latitude
				p.longitude = msg.longitude
				p.altitude  = msg.altitude
				p.stamp     = datetime.combine(date, msg.timestamp)
				
				points.add(p)
			except:
				# who cares :D
				continue
	return points

"""
GPX
"""
class GPXData(TruthData):

	# Should fill in the data from the folder
	def fromFolder(self, folder):
		points = set()
		for file in glob(folder + "**/*.gpx", recursive=True):
			points = points.union(set(getGPXpoints(file)))
		self.points = points

	def quickStats(self):
		return "GPX Quick Stats : [ " + str(len(self.points)) + " points ]"

def getGPXpoints(gpx_file_name):
	points = set()
	"""
	<trkpt lat="64.803741993382573" lon="-147.88129697553813">
		<ele>147.69999999999999</ele>
		<time>2021-01-29T01:06:56Z</time>
	</trkpt>
	"""
	with open(gpx_file_name, "r") as fr:
		lat, lon, ele, time = None, None, None, None
		for line in fr:
			
			if "<trkpt" in line and (lat == None and \
				                     lon == None and \
				                     ele == None and \
				                     time == None):

				lat = float(line.split("lat=\"")[1].split("\"")[0])
				lon = float(line.split("lon=\"")[1].split("\"")[0])
			
			elif "<ele" in line and (lat  != None and \
				                     lon  != None and \
				                     ele  == None and \
				                     time == None):

				ele = float(line.split("<ele>")[1].split("</ele>")[0])

			elif "<time" in line and (lat  != None and \
									  lon  != None and \
									  ele  != None and \
									  time == None):

				time = line.split("<time>")[1].split("</time>")[0]
				try:
					time = datetime.strptime(time, \
											 "%Y-%m-%dT%H:%M:%S.%fZ")
				except:
					time = datetime.strptime(time, \
											 "%Y-%m-%dT%H:%M:%SZ")

			if (lat != None and lon != None and ele != None and time != None):

				p = Point()

				p.stamp     = time
				p.latitude  = lat
				p.longitude = lon
				p.altitude  = ele 
				
				# ^ review this; is the elevation the same as altitude? TODO

				points.add(p)

				lat, lon, ele, time = None, None, None, None

	return points

"""
MAVLINK
"""

class MavlinkData(TruthData):

	# Should fill in the data from the folder
	def fromFolder(self, folder):
		points = set()
		for file in glob(folder + "**/*mavlink.log", recursive=True):
			points = points.union(set(getMavlinkPoints(file)))
		self.points = points

	def quickStats(self):
		return "Mavlink Quick Stats : [ " + str(len(self.points)) + " points ]"

def getMavlinkPoints(mavlink_file_name):
	points = []
	with open(mavlink_file_name, "r") as fr:
		stuff = json.loads(fr.read())
		for entry in stuff:
			(lat, lon, alt) = (entry["latitude"],  \
							   entry["longitude"], \
							   entry["altitude"])
			lat, lon = mavlinkCoords(lat, lon)
			alt = float(alt) / 100 # cm -> m
			time = None
			try:
				time = datetime.strptime(entry["timeStamp"], \
										 "%Y-%m-%dT%H:%M:%S.%fZ")
			except:
				time = datetime.strptime(entry["timeStamp"], \
										 "%Y-%m-%dT%H:%M:%SZ")
			if (lat, lon, alt) != (0.0, 0.0, 0.0):
				p = Point()

				p.stamp     = time
				p.latitude  = lat
				p.longitude = lon
				p.altitude  = alt

				points.append(p)
	return points

def fixBrokenMavlinkCoords(coord):
	if "E" in str(coord):
		a, b = s.split("E")
		a = float(a)
		b = int(b)
		c = a * 10 ** b
	else:
		c = float(coord)
	return c / ( 10 ** 7 )

def mavlinkCoords(lat, lon):
	lat = fixBrokenMavlinkCoords(str(lat))
	lon = fixBrokenMavlinkCoords(str(lon))
	return lat, lon