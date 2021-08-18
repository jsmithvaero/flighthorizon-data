"""
file    : dateParser.py
author  : Max von Hippel
authored: 18 August 2021
"""
from datetime import datetime

def parseDate(dateStr):
	# '2021-06-08T21:56:58.442844700Z'
	YMD, HMS = dateStr.split("T")
	year, month, day = YMD.split("-")
	year, month, day = int(year), int(month), int(day)
	hour, minute, second = (HMS.split("Z")[0]).split(":")
	hour, minute, second = int(hour), int(minute), int(second.split(".")[0])
	return datetime(
		year=year,
		month=month,
		day=day,
		hour=hour,
		minute=minute,
		second=second)