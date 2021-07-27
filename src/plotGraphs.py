import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.units as munits
import matplotlib.dates as mdates
import matplotlib.colors as colors
from mpl_toolkits import mplot3d
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.mplot3d import Axes3D
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
from deflate_dict import deflate
from dictances import *
from tabulate import tabulate
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.crs as ccrs

converter = mdates.ConciseDateConverter()
munits.registry[np.datetime64] = converter
munits.registry[date] = converter
munits.registry[datetime] = converter

mpl.rc('font', size=8)
cmap = mpl\
		.colors\
		.LinearSegmentedColormap.from_list("", ["red", "violet", "blue"])

norm = plt.Normalize(0, 100)

"""
This draws the main figure we try to build in this Python script.  The arguments
are:
lons    - list of longitudes
lats    - list of latitudes
alts    - list of altitudes
_c      - list of arguments w/ which to colorize the (lon, lat, alt) points
_cm     - color scale, indexed by _c
name    - name of the input data source, e.g., "Echoflight"
mindate - minimum date/time-stamp of the data
maxdate - maximum date/time-stamp of the data
"""
def draw_map_figure(lons, lats, alts, _c, _cm, name, mindate, maxdate, rcvrs=None):
	max_lat = max(lats)
	min_lat = min(lats)
	max_lon = max(lons)
	min_lon = min(lons)
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
	ax.set_ylabel('Latitude (°N)' , labelpad=20)
	ax.set_zlabel('Altitude (m)'  , labelpad=20)
	meridians = sorted(
					list(
						set(np.arange(min_lon, 
							          max_lon, 
							          (max_lon - min_lon) / 5))\
	            		.union({ min_lon, max_lon })))
	parallels = sorted(
					list(
						set(np.arange(min_lat, 
									  max_lat, 
									  (max_lat - min_lat) / 5))\
						.union({ min_lat, max_lat })))
	ax.set_yticks(parallels)
	ax.set_yticklabels(parallels)
	ax.set_xticks(meridians)
	ax.set_xticklabels(meridians)
	lon_formatter = LongitudeFormatter(zero_direction_label=True)
	lat_formatter = LatitudeFormatter()
	ax.xaxis.set_major_formatter(lon_formatter)
	ax.yaxis.set_major_formatter(lat_formatter)
	ax.tick_params(axis='x', which='major', pad=10)
	ax.tick_params(axis='y', which='major', pad=10)

	ax.set_zlim(0., 1000.)
	ax.scatter(lons,       \
		       lats,       \
		       alts,       \
		       c=_c,       \
		       marker=".", \
		       cmap=_cm)

	if rcvrs != None:
		ax.scatter([r["lat"] for r in rcvrs], 
			       [r["lon"] for r in rcvrs], 
			       [r["alt"] for r in rcvrs], marker='^')

	filename = name + ".from." + str(mindate) + ".to." + str(maxdate)
	newname = filename.replace("[", "_")\
					    .replace("]", "_")\
					    .replace(" ", "-")\
					    .replace("/", ".")\
					    .replace("\\", ".") + ".png"
	plt.savefig(newname, dpi=200)
	plt.close()
	print("\t.... saved to " + newname)
	return newname

"""
This function calls draw_map_figure() on both the radar and truth data.
It saves the resulting images with self-explanatory filenames.
Additionally, it computes a bunch of useful(?) metrics and pseudo-metrics,
and prints them to the terminal.  (It might not do that though if the inputs
seem malformed, check out the code ... it kind of intelligently avoids
empty or wack datasets.)
"""
def draw_3dmap(block_of_radar_points, \
			   mindate,               \
			   maxdate,               \
			   radarname,             \
			   block_of_truth_data,   \
			   rcvrs=None):

	radar_figure_file, truth_figure_file, metrics_table = None, None, None

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
	
	# RADAR
	if len(lats) * len(lons) > 0:
		min_lat = min(lats)
		max_lat = max(lats)
		min_lon = min(lons)
		max_lon = max(lons)
		radar_figure_file = draw_map_figure(\
						lons, \
			            lats, \
			            alts, \
			            [1 if t else 0 for t in truths], \
			            colors.ListedColormap(['green', 'red']), \
			            radarname, \
			            mindate,   \
			            maxdate,   \
			            rcvrs)
	
	# TRUTH
	if len(true_lats) * len(true_lons) > 0:
		truth_figure_file = draw_map_figure(\
						true_lons, \
						true_lats, \
						true_alts, \
						[(t - mindate).total_seconds() for t in true_times], \
						'jet',   \
						'truth', \
						mindate, \
						maxdate, \
						rcvrs)

	if len(lats) * len(lons) > 0 and len(true_lats) * len(true_lons) > 0:

		radar_dict = {
			(time - mindate).total_seconds() : {
				"lat" : lat,
				"lon" : lon,
				"alt" : alt
			} for (time, _, lat, lon, alt, _, _) in block_of_radar_points
		}

		truth_dict = {
			(time - mindate).total_seconds() : {
				"lat" : lat,
				"lon" : lon,
				"alt" : alt
			} for (time, lat, lon, alt)  in block_of_truth_data
		}

		print(str(len(radar_dict)) + " radar points.")
		print(str(len(truth_dict)) + " truth points.")

		deflated_radar = deflate(radar_dict)
		deflated_truth = deflate(truth_dict)

		bhattacharyya_tr     = bhattacharyya    (deflated_truth, deflated_radar)
		canberra_tr          = canberra         (deflated_truth, deflated_radar)
		chebyshev_tr         = chebyshev        (deflated_truth, deflated_radar)
		chi_square_tr        = chi_square       (deflated_truth, deflated_radar)
		cosine_tr            = cosine           (deflated_truth, deflated_radar)
		euclidean_tr         = euclidean        (deflated_truth, deflated_radar)
		hamming_tr           = hamming          (deflated_truth, deflated_radar)
		jensen_shannon_tr    = jensen_shannon   (deflated_truth, deflated_radar)
		kullback_leibler_tr  = kullback_leibler (deflated_truth, deflated_radar) 
		mae_tr               = mae              (deflated_truth, deflated_radar)
		manhattan_tr         = manhattan        (deflated_truth, deflated_radar)
		minkowsky_tr         = minkowsky        (deflated_truth, deflated_radar)
		mse_tr               = mse              (deflated_truth, deflated_radar)
		pearson_tr           = pearson          (deflated_truth, deflated_radar)
		squared_variation_tr = squared_variation(deflated_truth, deflated_radar)

		metrics = [
			["bhattacharyya"    , bhattacharyya_tr    ],
			["canberra"         , canberra_tr         ],
			["chebyshev"        , chebyshev_tr        ],
			["chi_square"       , chi_square_tr       ],
			["cosine"           , cosine_tr           ],
			["euclidean"        , euclidean_tr        ],
			["hamming"          , hamming_tr          ],
			["jensen_shannon"   , jensen_shannon_tr   ],
			["kullback_leibler" , kullback_leibler_tr ],
			["mae"              , mae_tr              ],
			["manhattan"        , manhattan_tr        ],
			["minkowsky"        , minkowsky_tr        ],
			["mse"              , mse_tr              ],
			["pearson"          , pearson_tr          ],
			["squared_variation", squared_variation_tr]
		]

		print("\tDistance(truth, radar)")
		metrics_string = str(tabulate(metrics, ["metric", "value"], tablefmt="fancy_grid"))
		print(metrics_string)
		metrics_table = metrics

	return radar_figure_file, truth_figure_file, metrics_table

"""
Makes some nice 2D scatter-plots.  Not currently in use.
"""
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

# Each row is of the form 
# radar_figure, truth_figure, metrics_string
def create_automated_report(rows_in_report):
	print("rows in report = ", rows_in_report)
	report_text = "# Flight Test Data Report"
	report_text += "\n## Automatically generated by `FlightHorizon-Analysis`."
	report_text += "\n\n"
	for row in rows_in_report:
		[rad, tru, tab] = row
		if (rad, tru, tab) != (None, None, None):
			report_text += "\n---\n"
			rad_str = "N/A"
			tru_str = "N/A"
			if rad != None:
				rad_str = "![](" + rad + ")"
			if tru != None:
				tru_str = "![](" + tru + ")"
			report_text += "\nRadar Data|Truth Data\n:-:|:-:\n" \
						 	+ rad_str \
						 	+ "|" \
						 	+ tru_str \
						 	+ "\n"
			if tab != None:
				report_text += "\n### Metrics\n"
				report_text += str(tabulate(tab, ["Metric", "Value"], tablefmt="pipe"))
	with open("AutomatedReport.md", "w") as fw:
		fw.write(report_text)
"""
Code for graphing matplotlib vectors
"""
"""
plot_vector 
Adapted some code from: https://stackoverflow.com/questions/27023068/plotting-3d-vectors-using-python-matplotlib
Input must be in the form of:
vector = np.array([[x, y, z, u, v, w], ...])
ax = an axis object made normally by:
ax = fig.add_subplot(111, projection='3d')
"""
def plot_vectors(vector, ax):
	x, y, z, u, v, w = zip(*vector)
	ax.quiver(x, y, z, u, v, w)
	max_len = max(np.abs(vector.flatten()))
	ax.set_xlim([-max_len, max_len])
	ax.set_ylim([-max_len, max_len])
	ax.set_zlim([-max_len, max_len])

def plot_vector_setup():
	ax = plt.figure().add_subplot(projection='3d')
	ax.set_xlabel('e')
	ax.set_ylabel('n')
	ax.set_zlabel('u')
	return ax

def plot_radar_fov_indicators(vector, fov, ax):
	x, y, z, u, v, w = zip(*vector)