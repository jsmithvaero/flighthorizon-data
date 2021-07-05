"""
file    : Question.py
author  : Max von Hippel
authored: 4 July 2021
purpose : To answer questions about the data.
"""
import traces
import pandas

class Question:

	timestamped_X = None 
	timestamped_Y = None 

	def __init__(self, timestamped_X=None, \
		               timestamped_Y=None, \
		               X_parser=None,      \
		               Y_parser=None,      \
		               BLOCK=None):
		
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

		self.timestamped_X = [ (s, x) for 
		                       (s, x) in self.timestamped_X 
		                              if inRange(s) ]

		self.timestamped_Y = [ (s, y) for 
		                       (s, y) in self.timestamped_Y 
		                              if inRange(s) ]

	"""
	Out plotXY() function will take the two timestamped series, and merge them
	into one, by interpolating on either side.

	There will be three kinds of points: X_interplated, Y_interplated, and
	XY_original.
	"""
	def plotXY(self):

		X_ts = traces.TimeSeries()
		Y_ts = traces.TimeSeries()

		for (stamp, x) in timestamped_X:
			X_ts[stamp] = x

		for (stamp, y) in timestamped_Y:
			Y_ts[stamp] = y

		regular_X = X_ts.moving_average(500, pandas=True)
		regular_Y = Y_ts.moving_agerage(500, pandas=True)

		pandas.DataFrame.plot.scatter(regular_X, regular_Y)




"""
-------------------------- Question Variable Parsers ---------------------------
"""

