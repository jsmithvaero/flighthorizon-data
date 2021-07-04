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

You might also want to have more metadata on *all* of your log files.
In this case, run:

````
make tables
````

## Structure

* `figures` contains code to produce some specific, pre-defined figures from `demo-data`
* `tables` contains code to produce some specific, pre-defined tables from `demo-data`
* `demo-data` contains some data from Alaska flight tests, with which to develop our code
* `src` contains our actual organized source-code.

Over time, small ad-hoc things from `figures` and `tables` will be removed from those folders once they have been fully and satisfactorally integrated into `src`.

## Some Works Cited

* https://stackoverflow.com/a/37738851/1586231
* https://stackoverflow.com/a/43211266/1586231
* https://stackoverflow.com/q/15908371/1586231
* https://matplotlib.org/3.1.1/gallery/subplots_axes_and_figures/subplot.html#sphx-glr-gallery-subplots-axes-and-figures-subplot-py
* https://stackoverflow.com/a/55690467/1586231
* https://www.kite.com/python/answers/how-to-find-the-distance-between-two-lat-long-coordinates-in-python
* https://medium.com/@lkhphuc/how-to-plot-a-3d-earth-map-using-basemap-and-matplotlib-2bc026483fe4