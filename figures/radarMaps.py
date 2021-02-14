# %matplotlib inline
"""
file       : timeline.py
author     : Max von Hippel
authored   : 14 February 2021
description: the purpose of this file is to make timeline infographics 
             illustrating data collection
works cited: https://stackoverflow.com/a/37738851/1586231
             https://stackoverflow.com/a/43211266/1586231
             https://stackoverflow.com/q/15908371/1586231
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
import json
from geopy import distance
from mpl_toolkits import mplot3d
import matplotlib.colors
import os

matplotlib.rc('font', size=12)
# matplotlib.rc('axes', titlesize=10)

demo_radar_file = \
	"../build/logs/alaska/01.26.21/linux/20210126T072518_radar.log"


# def two_plot(x, y1, name1, y2, name2):
def multi_plot(x, named_ys):
	fig = plt.figure()
	# set height ratios for subplots
	gs = gridspec.GridSpec(len(named_ys), 1, height_ratios=[1, 1]) 

	# the first subplot
	ax0 = plt.subplot(gs[0])
	# log scale for axis Y of the first subplot
	ax0.set_yscale("linear")

	(y1, name1) = named_ys[0]

	line0, = ax0.plot(x, y1, color='r')

	i = 1

	for (yi, namei) in named_ys[1:]:

		# the second subplot
		# shared axis X
		ax1 = plt.subplot(gs[i], sharex=ax0)
		line1, = ax1.plot(x, yi, color='b')
		plt.setp(ax0.get_xticklabels(), visible=False)
		# remove last tick label for the second subplot
		yticks = ax1.yaxis.get_major_ticks()
		yticks[-1].label1.set_visible(False)

	# put legend on first subplot
	# ax0.legend((line0, line1), (name1, name2), loc='lower left')

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

cmap = matplotlib\
		.colors\
		.LinearSegmentedColormap.from_list("", ["red", "violet", "blue"])

norm = plt.Normalize(0, 100)


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
		stuff = json.loads(fr.read())
		for entry in stuff:
			(x, y, z) = (entry["xest"], entry["yest"], entry["zest"])
			# dist = (x ** 2 + y ** 2 + z ** 2) ** 0.5
			time = entry["timeStamp"]
			conf = entry["confidenceLevel"]
			points.append((time, conf, x, y, z))
	return points

def plot_radar_points(radar_file_name):
	fig = plt.figure()
	fig.suptitle("RADAR data - " \
		+ os.path.basename(radar_file_name)\
			.replace(".log", ""))
	ax = plt.axes(projection='3d')
	ax.set_ylabel('Δy from RADAR')
	ax.set_xlabel('Δx from RADAR')
	ax.set_zlabel('Δz from RADAR')
	points = get_radar_points(radar_file_name)
	xline = [p[2] for p in points]
	yline = [p[3] for p in points]
	zline = [p[4] for p in points]
	cline = [p[1] for p in points]
	im = ax.scatter3D(xline, yline, zline, c=cline, cmap=cmap, norm=norm)
	cbar = fig.colorbar(im, ax=ax)
	cbar.set_label('Confidence', rotation=270)
	plt.show()

def plot_radar_xys(radar_file_name):
	points = get_radar_points(radar_file_name)
	xline = [p[0] for p in points]
	distline = [(p[2] ** 2 + p[3] ** 2 + p[4] ** 2) ** 0.5 for p in points]
	confline = [p[1] for p in points]
	# two_plot(xline, distline, "Distance from RADAR", confline, "Confidence")
	multi_plot(xline, [(distline, "Distance from RADAR"), \
					   (confline, "Confidence")])

# Simple data to display in various forms
# x = np.linspace(0, 2 * np.pi, 400)
# y1 = np.sin(x ** 2)
# y2 = np.cos(x ** 3)

# two_plot(x, y1, y2)

# plot_radar_points(demo_radar_file)



plot_radar_xys(demo_radar_file)