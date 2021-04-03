# FlightHorizon Analysis

The purpose of this repository is to house data analysis software written and 
used by Vigilant Aerospace for the express purpose of analyzing flight data.

A couple of notes.

1. Please refer to the Makefile for an explanation of how to run the code.
2. Most of the code being actively used and developed is in `radarFigs.py`.
3. It appears that at least one of the computers we used to log data had AM and PM
swapped on accident, i.e. was off by 12 hours, and so you should interpret the
timestamps by subtracting 12 hours.
4. A lot of the Mavlink log files are a bit strange in their formatting, see 
parser logic in `radarFigs.py` for more details.

To get started:

````
make clean deps figures
````