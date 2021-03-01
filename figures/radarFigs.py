# %matplotlib inline
"""
file	   : radarFigs.py
author	 : Max von Hippel
authored   : 14 February 2021
description: the purpose of this file is to make timeline infographics 
			 illustrating data collection
works cited: https://stackoverflow.com/a/37738851/1586231
			 https://stackoverflow.com/a/43211266/1586231
			 https://stackoverflow.com/q/15908371/1586231
			 https://matplotlib.org/3.1.1/gallery/subplots_axes_and_figures/
			 		 subplot.html#sphx-glr-gallery-subplots-axes-and-figures
			 		 -subplot-py
			 https://stackoverflow.com/a/55690467/1586231
			 https://www.kite.com/python/answers/how-to-find-the-distance-
			 		 between-two-lat-long-coordinates-in-python
			 https://medium.com/@lkhphuc/how-to-plot-a-3d-earth-map-using-
			 		 basemap-and-matplotlib-2bc026483fe4
usage	  : python3 figures/radarMaps.py ../build/logs/alaska/01.29.21/
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.units as munits
import matplotlib.dates as mdates
import matplotlib.colors as colors
from mpl_toolkits import mplot3d
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.mplot3d import Axes3D
from geopy import distance
import pynmea2
import numpy as np
import json
import os
import sys
import math
import ntpath
from datetime import datetime, date
from glob import glob
import traceback

converter = mdates.ConciseDateConverter()
munits.registry[np.datetime64] = converter
munits.registry[date] = converter
munits.registry[datetime] = converter

mpl.rc('font', size=8)
# matplotlib.rc('axes', titlesize=10)

demo_radar_file = \
	"../build/logs/alaska/01.26.21/linux/20210126T072518_radar.log"

def PAC(time, lat, lon, alt, truth):
	for (time_truth, lat_truth, lon_truth, alt_truth) in truth:
		if ((time_truth - time).total_seconds() <= 60):
			continue
		if (distance_km(lat_truth, lon_truth, lat, lon) / 1000) > 10:
			continue
		if (abs(alt - alt_truth) > 10):
			continue
		return True
	return False

def draw_map_figure(lons, lats, alts, _c, _cm, name, mindate, maxdate, min_lon, max_lon, min_lat, max_lat):
	fig = plt.figure()
	fig.suptitle(name + " " + str(mindate) + " to " + str(maxdate))
	ax = fig.gca(projection='3d')
	bm = Basemap(
		llcrnrlon=min_lon, 
		llcrnrlat=min_lat,
        urcrnrlon=max_lon, 
        urcrnrlat=max_lat,
        projection='cyl', 
        resolution='l', 
        fix_aspect=False, 
        ax=ax) 
	ax.view_init(azim=230, elev=50)
	ax.set_xlabel('Longitude (°E)', labelpad=20)
	ax.set_ylabel('Latitude (°N)', labelpad=20)
	ax.set_zlabel('Altitude (m)', labelpad=20)
	lon_step = 30
	lat_step = 30
	meridians = np.arange(min_lon, max_lon + lon_step, lon_step)
	parallels = np.arange(min_lat, max_lat + lat_step, lat_step)
	ax.set_yticks(parallels)
	ax.set_yticklabels(parallels)
	ax.set_xticks(meridians)
	ax.set_xticklabels(meridians)
	ax.set_zlim(0., 1000.)
	ax.scatter(lons, \
		       lats, \
		       alts, \
		       c=_c, \
		       marker=".", \
		       cmap=_cm)
	filename = name + ".from." + str(mindate) + ".to." + str(maxdate)
	plt.savefig(filename.replace("[", "_")\
					    .replace("]", "_")\
					    .replace(" ", "-")\
					    .replace("/", ".")\
					    .replace("\\", ".") + ".png", dpi=200)
	plt.close()

def draw_3dmap(block_of_radar_points, mindate, maxdate, radarname, block_of_truth_data):
	print("draw_3dmap(...", mindate, maxdate, radarname, ")")
	true_lons, true_lats, true_alts, true_times = [], [], [], []
	for (t_time, t_lat, t_lon, t_alt) in block_of_truth_data:
		true_lons.append(t_lon)
		true_lats.append(t_lat)
		true_alts.append(t_alt)
		true_times.append(t_time)
	
	# (time, conf, lat, lon, alt, dist)
	lats, lons, alts, confs = [], [], [], []
	goods = 0
	bads = 0
	truths = []
	for (time, conf, lat, lon, alt, dist, truth) in block_of_radar_points:
		lats.append(lat)
		lons.append(lon)
		alts.append(alt)
		confs.append(conf)
		truths.append(truth)
		if truth:
			goods += 1
		else:
			bads += 1
	print(goods, bads)
	min_lat = min(lats)
	max_lat = max(lats)
	min_lon = min(lons)
	max_lon = max(lons)
	if ((min_lat >= max_lat) or (min_lon >= max_lon)):
		return
	
	draw_map_figure(lons, \
		            lats, \
		            alts, \
		            [1 if t else 0 for t in truths], \
		            colors.ListedColormap(['green', 'red']), \
		            radarname, \
		            mindate,   \
		            maxdate,   \
		            min_lon,   \
		            max_lon,   \
		            min_lat,   \
		            max_lat)
	draw_map_figure(true_lons, \
					true_lats, \
					true_alts, \
					[(t - mindate).total_seconds() for t in true_times], \
					'jet',   \
					'truth', \
					mindate, \
					maxdate, \
					min_lon, \
					max_lon, \
					min_lat, \
					max_lat)


def calculateTargetBearing(_azimuth, _radar_orientation):
	tmp_bearing = None
	if (_azimuth <= 0):
		tmp_bearing = -1 * _azimuth
	else:
		tmp_bearing = 360 - _azimuth
	return tmp_bearing + _radar_orientation

# def two_plot(x, y1, name1, y2, name2):
def multi_plot(name, x, named_ys):
	fig = plt.figure()
	fig.suptitle(name)
	# set height ratios for subplots
	K = 1 if len(named_ys) <= 3 else 2
	gs = gridspec.GridSpec(\
		len(named_ys), \
		1, \
		height_ratios=[K] * len(named_ys)) 

	# the first subplot
	ax0 = plt.subplot(gs[0])
	# log scale for axis Y of the first subplot
	ax0.set_yscale("linear")
	ax0.xaxis.set_visible(False)

	(xbase, y1, name1) = named_ys[0]

	line0, = ax0.plot(xbase, y1, 'o', color='r')
	plt.ylabel(name1, rotation='horizontal', ha='right', labelpad=20)

	i = 1

	colors = ['green', 'blue', 'black', 'purple']

	last = len(named_ys) - 1

	for (xi, yi, namei) in named_ys[1:]:

		# the second subplot
		# shared axis X
		ax1 = plt.subplot(gs[i], sharex=ax0)
		plt.ylabel(namei, rotation='horizontal', ha='right', labelpad=20)
		line1, = ax1.plot(xi, yi, 'o', color=colors[i % 4])
		plt.setp(ax0.get_xticklabels(), visible=False)
		ax1.xaxis.set_major_locator(plt.MaxNLocator(20))
		ax1.xaxis.set_visible(i == last)
		# plt.xticks(rotation=60)
		# remove last tick label for the second subplot
		yticks = ax1.yaxis.get_major_ticks()
		yticks[-1].label1.set_visible(False)
		i += 1

	# put legend on first subplot
	# ax0.legend((line0, line1), (name1, name2), loc='lower left')

	# remove vertical gap between subplots
	plt.subplots_adjust(hspace=.0)
	plt.xticks(rotation=60)
	plt.tight_layout()

	# plt.show()
	plt.savefig(name.replace("[", "_")\
					.replace("]", "_")\
					.replace(" ", "-")\
					.replace("/", ".")\
					.replace("\\", ".") + ".png", dpi=200)

def get_config_name(radar_file_name):
	try:
		radar_config_file_name = radar_file_name.replace(".log", "_config.log")
		with open(radar_config_file_name, "r") as fr:
			stuff = json.loads(fr.read())
			return stuff["name"]
	except:
		return None

def get_config_location(radar_file_name):
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

# https://stackoverflow.com/a/7835325/1586231
def calculateTargetPosition(_range, _azimuth, _elevation, receiver):
	(lat1, lon1, alt1, radar_orientation) = receiver
	# print("lat1:", lat1, " degrees")
	# print("lon1:", lon1, " degrees")
	# print("alt1:", alt1, " meters")
	# print("radar orientation:", radar_orientation, " degrees")
	
	horizontal_distance = _range * math.cos(math.radians(_elevation)) # METERs
	vertical_distance   = _range * math.sin(math.radians(_elevation)) # METERs
	bearing			 = calculateTargetBearing(_azimuth, radar_orientation) # DEGREE_ANGLE

	# print("horizontal_distance:", horizontal_distance, " meters")
	# print("vertical_distance:", vertical_distance, " meters")
	# print("bearing:", bearing, " degrees")

	R = 6.371009 * (10 ** 6) + alt1

	# print("R:", R, " meters")

	bearing_radians = math.radians(bearing)

	# print("bearing_radians: ", bearing_radians)

	lat1 = math.radians(lat1)
	lon1 = math.radians(lon1)
	
	lat2 = math.asin(
		math.sin(lat1) * math.cos(horizontal_distance / R) +
		math.cos(lat1) * math.sin(horizontal_distance / R) * math.cos(bearing_radians))

	lon2 = lon1 + math.atan2(
				math.sin(bearing_radians) * math.sin(horizontal_distance / R) * math.cos(lat1),
			 	math.cos(horizontal_distance / R) - math.sin(lat1) * math.sin(lat2))

	lat2 = math.degrees(lat2)
	lon2 = math.degrees(lon2)
	alt2 = alt1 + vertical_distance

	# print("lat2:", lat2)
	# print("lon2:", lon2)
	# print("alt2:", alt2)

	return (lat2, lon2, alt2)

def distance_km(lat1, lon1, lat2, lon2):
	if (lat1, lon1) == (lat2, lon2):
		return 0
	R = 6373.0 # radius of the Earth in km
	lat1 = math.radians(lat1)
	lon1 = math.radians(lon1)
	lat2 = math.radians(lat2)
	lon2 = math.radians(lon2)
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	
	# Haversine formula
	a = math.sin(dlat / 2) ** 2 \
	  + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2

	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	
	distance = R * c

	return distance

cmap = mpl\
		.colors\
		.LinearSegmentedColormap.from_list("", ["red", "violet", "blue"])

norm = plt.Normalize(0, 100)

# TYPE: [ ... (time, conf, lat, lon, alt, dist) ...]
def get_radar_points(radar_file_name):
	receiver = get_config_location(radar_file_name)
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
			dist = distance_km(lat, lon, receiver[0], receiver[1])
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

def fix_crappy_mavlink_coordinate(coord):
	if "E" in str(coord):
		a, b = s.split("E")
		a = float(a)
		b = int(b)
		c = a * 10 ** b
	else:
		c = float(coord)
	return c / ( 10 ** 7 )

def mavlink_coords(lat, lon):
	lat = fix_crappy_mavlink_coordinate(str(lat))
	lon = fix_crappy_mavlink_coordinate(str(lon))
	return lat, lon

# TYPE: [... (time, lat, lon, alt) ...]
def get_mavlink_points(mavlink_file_name):
	points = []
	with open(mavlink_file_name, "r") as fr:
		stuff = json.loads(fr.read())
		for entry in stuff:
			(lat, lon, alt) = (entry["latitude"],  \
							   entry["longitude"], \
							   entry["altitude"])
			lat, lon = mavlink_coords(lat, lon)
			alt = float(alt) / 100 # cm -> m
			time = None
			try:
				time = datetime.strptime(entry["timeStamp"], \
										 "%Y-%m-%dT%H:%M:%S.%fZ")
			except:
				time = datetime.strptime(entry["timeStamp"], \
										 "%Y-%m-%dT%H:%M:%SZ")
			if (lat, lon, alt) != (0.0, 0.0, 0.0):
				points.append((time, lat, lon, alt))
	return points

def get_adsb_points(adsb_file_name):
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
				points.append((time, lat, lon, alt))
	return points

def get_nmea_points(nmea_file_name, date):
	points = set()
	with open(nmea_file_name, "r", encoding='utf-8') as fr:
		for line in fr:
			try:
				msg = pynmea2.parse(line)
				lat = msg.latitude
				lon = msg.longitude
				alt = msg.altitude
				time = datetime.combine(date, msg.timestamp)
				points.add((time, lat, lon, alt))
			except:
				# who cares :D
				continue
	return points

def get_gpx_ponts(gpx_file_name):
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
			if "<trkpt" in line and (lat == None and lon == None and ele == None and time == None):
				lat = float(line.split("lat=\"")[1].split("\"")[0])
				lon = float(line.split("lon=\"")[1].split("\"")[0])
			elif "<ele" in line and (lat != None and lon != None and ele == None and time == None):
				ele = float(line.split("<ele>")[1].split("</ele>")[0])
			elif "<time" in line and (lat != None and lon != None and ele != None and time == None):
				time = line.split("<time>")[1].split("</time>")[0]
				try:
					time = datetime.strptime(time, \
											 "%Y-%m-%dT%H:%M:%S.%fZ")
				except:
					time = datetime.strptime(time, \
											 "%Y-%m-%dT%H:%M:%SZ")
			if (lat != None and lon != None and ele != None and time != None):
				points.add((time, lat, lon, ele))
				lat, lon, ele, time = None, None, None, None
	return points

def get_many_nmea_points(nmea_path):
	points = set()
	for file in glob(nmea_path + "**/*.nmea", recursive=True):
		if "_" in file:
			year, month, day, _ = ntpath.basename(file).split("_", 3)
			year = int(year)
			month = int(month)
			day = int(day)
		points = points.union(      \
					get_nmea_points(\
						file,       \
						date(year, month, day)))
	return points

def get_many_gpx_points(gpx_path):
	points = set()
	for file in glob(gpx_path + "**/*.gpx", recursive=True):
		points = points.union(set(get_gpx_ponts(file)))
	return points

def get_many_mavlink_points(mavlink_path):
	points = set()
	for file in glob(mavlink_path + "**/*mavlink.log", recursive=True):
		points = points.union(set(get_mavlink_points(file)))
	return points

def get_many_radar_points(\
	radar_path, default="echoguard"):
	points = {}
	# print(radar_path)
	for file in glob(radar_path + "**/*radar.log", recursive=True):
		subpoints = get_radar_points(file)
		if subpoints != None:
			subname = get_config_name(file)
			if subname == None:
				subname = default
			if subname in points:
				points[subname] += subpoints
			else:
				points[subname] = subpoints
	return points

def get_many_adsb_points(adsb_path):
	points = set()
	for file in glob(adsb_path + "**/*adsb.log", recursive=True):
		points = points.union(set(get_adsb_points(file)))
	return points

def plot_radar_xyz(points, truth=None):
	stuff_to_plot = []
	
	_xline = set()
	for key, value in points.items():
		for p in value:
			_xline.add(p[0])
	xline = sorted(list(_xline))
	xindex = { }
	i = 0
	for p in xline:
		xindex[p] = i
		i += 1

	n = len(xline)

	if truth != None:
		# TYPE: [... (time, lat, lon, alt) ...]
		truth_timeline = [p[0] for p in truth]
		truth_latline  = [p[1] for p in truth]
		truth_lonline  = [p[2] for p in truth]
		truth_altline  = [p[3] for p in truth]
		stuff_to_plot.append((truth_timeline, truth_latline, "True Degrees\nLatitude"))
		stuff_to_plot.append((truth_timeline, truth_lonline, "True Degrees\nLongitude"))
		stuff_to_plot.append((truth_timeline, truth_altline, "True Altitude (m)"))

	for key, value in points.items():

		# (time, confidence, lat, lon, alt, distance)

		altline   = [p[4] for p in value]
		distline  = [p[5] for p in value]
		confline  = [p[1] for p in value]
		sub_xline = [p[0] for p in value]

		stuff_to_plot.append((sub_xline, distline, "Horizontal\nDistance (km)\nfrom " + key))
		stuff_to_plot.append((sub_xline, altline, "Altitude (m)\nabove " + key))
		stuff_to_plot.append((sub_xline, confline, "Confidence of\n" + key))

	# Let's break the data into blocks.
	blocks = [[xline[0]]]
	for j in range(1, len(xline)):
		if ((xline[j] - xline[j - 1]).total_seconds() / 60) > 10:
			blocks.append([])
		blocks[-1].append(xline[j])

	print("NUMBER OF BLOCKS = " + str(len(blocks)))

	for block in blocks:
		begin = block[0]
		end = block[-1]
		stuff_to_plot_in_block = []
		for stuff in stuff_to_plot:
			sub_stuff = []
			for i in range(len(stuff[0])):
				x = stuff[0][i]
				y = stuff[1][i]
				if x >= begin and x <= end:
					sub_stuff.append((x, y))
			if len(sub_stuff) > 0:
				stuff_to_plot_in_block.append(([x for x, _ in sub_stuff], \
											   [y for _, y in sub_stuff], \
											   stuff[2]))
		multi_plot("Radars " + str(begin.time().strftime("%H:%M:%S")) \
							 + " - "								  \
							 + str(end.time().strftime("%H:%M:%S"))   \
							 + ", "								   \
							 + str(begin.date()),					 \
			block,
			stuff_to_plot_in_block)

def block_split_time_indexed_data(data):
	sorted_data = sorted(data, key=lambda d : d[0])
	blocks = [[sorted_data[0]]]
	data_length = len(data)
	for j in range(1, data_length):
		if ((sorted_data[j][0] - sorted_data[j - 1][0]).total_seconds() / 60) > 10:
			blocks.append([sorted_data[j]])
		else:
			blocks[-1].append(sorted_data[j])
	return blocks

path_to_search = sys.argv[1]
full_radar_data = get_many_radar_points(path_to_search)
full_truth_data = get_many_mavlink_points(path_to_search)\
				  .union(get_many_adsb_points(path_to_search))\
				  .union(get_many_gpx_points(path_to_search))\
				  .union(get_many_nmea_points(path_to_search))

# plot_radar_xyz(full_radar_data, full_truth_data)

for k in full_radar_data:
	print("Working on " + str(k))
	k_blocks = block_split_time_indexed_data(full_radar_data[k])
	truth_blocks = []
	for block in k_blocks:
		mintime = block[0][0]
		maxtime = block[-1][0]
		truth_block = []
		for (time, lat, lon, alt) in full_truth_data:
			if ((mintime <= time) and (time <= maxtime)):
				truth_block.append((time, lat, lon, alt))
		truth_blocks.append(truth_block)
	for i in range(len(k_blocks)):
		block = k_blocks[i]
		truth_block = truth_blocks[i]
		print("\tBlock " + str(block[0][0]) + " to " + str(block[-1][0]))
		flattened_radar = [(time, conf, lat, lon, alt, dist,\
		                    PAC(time, lat, lon, alt, full_truth_data)) \
						   for (time, conf, lat, lon, alt, dist) in block]
		try:
			draw_3dmap(flattened_radar, block[0][0], block[-1][0], k, truth_block)
		except:
			traceback.print_exc()