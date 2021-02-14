%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

logs = "../build/logs/alaska/"

for file in glob.glob(logs + "**/*radar.log", recursive=True):
	# TODO
	
	# points = []
	# with open(file, "r") as fr:
	# 	stuff = json.loads(fr.read())
	# 	for row in stuff:
	# 		lat, lon, pid = row[]
	# m = Basemap(projection='lcc', resolution=None,
 #            width=8E6, height=8E6, 
 #            lat_0=45, lon_0=-100,)
	# m.etopo(scale=0.5, alpha=0.5)

	# x, y = m(-122.3, 47.6)
	# plt.plot(x, y, 'ok', markersize=5)
	# plt.text(x, y, ' Seattle', fontsize=12);
