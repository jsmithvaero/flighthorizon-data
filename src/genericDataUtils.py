"""
file    : genericDataUtils.py
author  : Max von Hippel
authored: 4 July 2021
purpose : Provides non-mathematical utils that are useful for more than one Data 
          class.
"""

"""
INPUT : log_file_name    - the file name of the log file to be parsed
OUTPUT: config_file_name - the name of the corresponding config file, or None,
                           if no such file exists
"""
def getConfigName(log_file_name):
	try:
		config_file_name = log_file_name.replace(".log", "_config.log")
		with open(config_file_name, "r") as fr:
			stuff = json.loads(fr.read())
			return stuff["name"]
	except:
		return None