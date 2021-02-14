"""
file       : timeline.py
author     : Max von Hippel
authored   : 14 February 2021
description: the purpose of this file is to make timeline infographics 
             illustrating data collection
works cited: some code adapted from https://stackoverflow.com/a/37738851/1586231
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

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

# Simple data to display in various forms
x = np.linspace(0, 2 * np.pi, 400)
y1 = np.sin(x ** 2)
y2 = np.cos(x ** 3)

two_plot(x, y1, y2)