import glob
import json
import os
from tabulate import tabulate
from datetime import datetime
import ntpath
import sys


logs = sys.argv[1]
day_to_contents = {}

rows = {}
icaos = {}

for file in glob.glob(logs + "**/*adsb.log", recursive=True):
	config = file.replace(".log", "_config.log")
	protocol = "unknown"
	if os.path.isfile(config):
		with open(config, "r") as fr:
			config_stuff = json.loads(fr.read())
			protocol = config_stuff['name']
	print(file + " was recorded with " + protocol)

	with open(file, "r") as fr:
		stuff = json.loads(fr.read())
		ids = [row['icaoAddress'] for row in stuff]
		times = set()
		for row in stuff:
			stamp = row['timeStamp']
			try:
				the_stamp = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
				times.add(the_stamp)
			except:
				the_stamp = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
				times.add(the_stamp)
		mintime = min(times)
		maxtime = max(times)
		_range = (maxtime-mintime).total_seconds()/60
		day = ((str(file).split('alaska'))[1]).split('/')[1]
		n = len(set(ids))
		if day in day_to_contents:
			day_to_contents[day].append((file, n))
		else:
			day_to_contents[day] = [(file, n)]
		new_row = [ntpath.basename(file), protocol, n, str(mintime.time()).split(".")[0], str(maxtime.time()).split(".")[0], str(_range), str(n/_range), "windows" if "windows" in file else "linux" if "linux" in file else "unknown"]
		if day in rows:
			rows[day].append(new_row)
			icaos[day] += ids
		else:
			rows[day] = [new_row]
			icaos[day] = ids

for day, contents in rows.items():
	print(day + " - saw icaos: " + ",".join(list(set(icaos[day]))))
	print(tabulate(sorted(contents), headers=["File", "Protocol", "Number of ICAOs", "First Packet", "Last Packet", "Minutes First to Last", "ICAOs/Minute", "OS"]))
# for day, contents in day_to_contents.items():
# 	print(str(day) + ":")
# 	for (file, num) in day_to_contents[day]:
# 		print("\t" + str(num) + " tracks recorded in " + file) 
# 	print("= " + str(sum([num for (file, num) in day_to_contents[day]])) + " tracks recorded on " + str(day))