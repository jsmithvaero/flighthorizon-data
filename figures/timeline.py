"""
file       : timeline.py
author     : Max von Hippel
authored   : 14 February 2021
description: the purpose of this file is to make timeline infographics 
             illustrating data collection
works cited: https://stackoverflow.com/a/37738851/1586231
             https://stackoverflow.com/a/43211266/1586231
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
import json
from geopy import distance

def two_plot(x, y1, y2):
	fig = plt.figure()
	# set height ratios for subplots
	gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1]) 

	# the first subplot
	ax0 = plt.subplot(gs[0])
	# log scale for axis Y of the first subplot
	ax0.set_yscale("log")
	line0, = ax0.plot(x, y1, color='r')

	# the second subplot
	# shared axis X
	ax1 = plt.subplot(gs[1], sharex = ax0)
	line1, = ax1.plot(x, y2, color='b', linestyle='--')
	plt.setp(ax0.get_xticklabels(), visible=False)
	# remove last tick label for the second subplot
	yticks = ax1.yaxis.get_major_ticks()
	yticks[-1].label1.set_visible(False)

	# put legend on first subplot
	ax0.legend((line0, line1), ('red line', 'blue line'), loc='lower left')

	# remove vertical gap between subplots
	plt.subplots_adjust(hspace=.0)
	plt.show()

def get_config_location(radar_file_name):
	radar_config_file_name = radar_file_name.replace(".log", "_config.log")
	lat, lon = None, None
	with open(radar_config_file_name, "r") as fr:
		stuff = json.loads(fr.read())
		lon = stuff["longitude"]["value"]
		lat = stuff["latitude"]["value"]
		assert("°".equals(stuff["longitude"]["unit"]))
		assert("°".equals(stuff["latitude"]["unit"]))
	return lat, lon

def distance_km(lat1, lon1, lat2, lon2):
	return distance.distance(lat1, lon1, lat2, lon2).km

"""
{"id":"-2147483648",
 "protocol":null,
 "state":0,
 "azest":0.0,
 "elest":0.0,
 "rest":0.0,
 "xest":0.0,
 "yest":0.0,
 "zest":0.0,
 "velxest":0.0,
 "velyest":0.0,
 "velzest":0.0,
 "associatedMeasurementIDs":[],
 "tocaDays":0,
 "tocaMilliseconds":0,
 "doca":0.0,
 "lifetime":0.0,
 "lastUpdateTimeDays":0,
 "lastUpdateTimeMilliseconds":0,
 "lastAssociatedDataTimeInDays":0,
 "lastAssociatedDataTimeInMilliseconds":0,
 "acquiredTimeDays":0,
 "acquiredTimeMilliseconds":0,
 "confidenceLevel":0.0,
 "numberOfMeasurements":0,
 "estRCS":0.0,
 "probUnknown":0.0,
 "probUAV":0.0,
 "timeStamp":"2021-01-26T19:14:44.518Z"}
"""
def get_radar_points(radar_file_name):
	points = []
	with open(radar_file_name, "r") as fr:
		stuff = json.loads(fr)
		for entry in stuff:
			(x, y, z) = (entry["xest", "yest", "zest"])
			# dist = (x ** 2 + y ** 2 + z ** 2) ** 0.5
			time = entry["timeStamp"]
			conf = entry["confidenceLevel"]
			points.append(time, conf, x, y, z)
	print(points)

# Simple data to display in various forms
x = np.linspace(0, 2 * np.pi, 400)
y1 = np.sin(x ** 2)
y2 = np.cos(x ** 3)

two_plot(x, y1, y2)