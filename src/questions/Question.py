"""
file    : Question.py
author  : Max von Hippel
authored: 4 July 2021
purpose : To answer questions about the data.
"""
import traces
import pandas
import matplotlib.pyplot as plt

from src.mathUtils import PAC

class Question:

	timestamped_X = None 
	timestamped_Y = None 

	def __init__(self, timestamped_X=None, \
		               timestamped_Y=None, \
		               X_parser=None,      \
		               Y_parser=None,      \
		               BLOCK=None,         \
		               X_axis_name=None,   \
		               Y_axis_name=None):
		
		if timestamped_X != None:
			self.timestamped_X = timestamped_X

		elif X_parser != None and BLOCK != None:
			self.timestamped_X = X_parser(BLOCK)

		else:
			assert(False) # ERROR! Ill-defined question.
		
		if timestamped_Y != None:
			self.timestamped_Y = timestamped_Y

		elif Y_parser != None and BLOCK != None:
			self.timestamped_Y = Y_parser(BLOCK)

		else:
			assert(False) # ERROR! Ill-defined question.

		self.removeIsolatedPoints()

		self.X_axis_name = X_axis_name
		self.Y_axis_name = Y_axis_name

	def removeIsolatedPoints(self):

		min_stamp = max({
			min([ s for (s, _) in self.timestamped_X ]),
			min([ s for (s, _) in self.timestamped_Y ])
		})

		max_stamp = min({
			max([ s for (s, _) in self.timestamped_X ]),
			max([ s for (s, _) in self.timestamped_Y ])
		})

		inRange = lambda s : min_stamp <= s and s <= max_stamp

		print("self.timestamped_X had size " + str(len(self.timestamped_X)))

		self.timestamped_X = [ (s, x) for 
		                       (s, x) in self.timestamped_X 
		                              if inRange(s) ]

		print("Now, self.timestamped_X has size " 
			  + str(len(self.timestamped_X)))

		print("self.timestamped_Y had size " + str(len(self.timestamped_Y)))

		self.timestamped_Y = [ (s, y) for 
		                       (s, y) in self.timestamped_Y 
		                              if inRange(s) ]

		print("Now, self.timestamped_Y has size " 
			  + str(len(self.timestamped_Y)))

	"""
	Out plotXY() function will take the two timestamped series, and merge them
	into one, by interpolating on either side.

	There will be three kinds of points: X_interplated, Y_interplated, and
	XY_original.
	"""
	def plotXY(self):

		X_ts = traces.TimeSeries()
		Y_ts = traces.TimeSeries()

		for (stamp, x) in self.timestamped_X:
			X_ts[stamp] = x

		for (stamp, y) in self.timestamped_Y:
			Y_ts[stamp] = y

		regular_X = X_ts.moving_average(10, pandas=True)
		regular_Y = Y_ts.moving_average(10, pandas=True)

		xAx = "Unknown X" if self.X_axis_name == None else self.X_axis_name
		yAx = "Unknown Y" if self.Y_axis_name == None else self.Y_axis_name

		title = xAx + " versus " + yAx

		plt.title  (title               )
		plt.xlabel (xAx                 )
		plt.ylabel (yAx                 )
		plt.scatter(regular_X, regular_Y)
		plt.show   (                    )


"""
-------------------------- Question Variable Parsers ---------------------------
"""

def distancesFromRadarParser(RD):
	ret = []
	for (stamp, conf, alt, lat, lon, dist) in RD.getPoints():
		ret.append((stamp, dist)) 
	return sorted(ret)

def confidencesOfRadar(RD):
	ret = []
	for (stamp, conf, alt, lat, lon, dist) in RD.getPoints():
		ret.append((stamp, conf)) 
	return sorted(ret)

def altitudesOfRadarTarget(RD):
	ret = []
	for (stamp, conf, alt, lat, lon, dist) in RD.getPoints():
		ret.append((stamp, alt)) 
	return sorted(ret)

def frequenciesOfValidRadarPoints(RD, TD):
	pac_points = []
	for (stamp, conf, alt, lat, lon, dist) in RD.getPoints():
		if PAC(stamp, lat, lon, alt, TD.getPoints()):
			pac_points.append((stamp, conf, alt, lat, lon, dist))
	stamped_second_window_frequencies = []
	for (stamp, conf, alt, lat, lon, dist) in pac_points:
		second_window = [
			s for s in pac_points
			if abs((stamp - s[0]).total_seconds()) <= 1 
			and s != (stamp, conf, alt, lat, lon, dist) 
		]
		frequency = len(second_window)
		stamped_second_window_frequencies.append((stamp, frequency))
	return stamped_second_window_frequencies
