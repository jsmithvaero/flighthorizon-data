"""
file    : plotTTDs.py
author  : Max von Hippel
authored: 20 August 2021
"""
import matplotlib.pyplot as plt

def plotTTDs(ttds):

	radarLogs = list(set([ttd[0] for ttd in ttds]))
	truthLogs = list(set([ttd[0] for ttd in ttds]))

	for radarLog in radarLogs:

		data = { 
			truth : [
				r for row in ttds
				for r in row[2:]
				if row[0] == radarLog and
				   row[1] == truthLog
			]
		}

		names = list(data.keys())
		values = list(data.values())

		plt.scatter(names, values)
		plt.title(radarLog)

		plt.xticks(rotation=45)

		plt.show()

def plotTTDsFromCLIoutput():
	cliOutput = "ttds.txt"
	ttds = []
	with open(cliOutput, "r") as fr:
		for line in fr:
			if not "[TTD] " in line:
				continue
			rem = line.split("[TTD] ")[1]
			parts = rem.split(",")
			parts = [ parts[0], parts[1] ] + [
				int(p) for p in parts[1:]
			]
			ttds.append(parts)
	plotTTDs(ttds)