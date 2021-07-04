"""
file    : Data.py
author  : Max von Hippel
authored: 4 July 2021
purpose : provides an abstract class for data
"""

class Data:
	# Should initialize the Data
	def __init__(self, folder=None, points=None):

		# We don't want to double check that the points come
		# from the folder, so, we should expect just one or the
		# other of the two options.
		assert(folder == None or points == None)
		
		# If the points are pre-defined, then we're Gucci.
		if folder == None and points != None:
			self.points = points

		# Otherwise if the folder is pre-defined, we can use that.
		elif folder != None and points == None:
			self.fromFolder(folder)

		# Final case is neither is defined and we will fill it in
		# later.
		else:
			self.points = None 

	# Should fill in the data from the folder
	def fromFolder(self, folder):
		pass 

	# Should return the current contents
	def getPoints(self):
		return self.points

	# Should return the current format
	def getFormat(self):
		pass

	# Should return some quick stats, for debugging.
	def quickStats(self):
		return ""
