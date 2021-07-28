"""
file    : radarInFovTestFunctions.py
author  : Levi Purdy
authored: 2021-07-21
purpose : Test functions for radar in FoV functions
"""

from src.radarData import *
import datetime


def main():
    print("Running radar fov test functions")
    # Range format:
    """
    #(time, conf, lat, lon, alt, dist, velVert, velX, velY, az, el, rn, radar_file_name)
	"""
    testRange = []

    testRange.append((datetime.datetime(2021, 1, 27, 20, 3, 20, 88000), 0.0, 65.12624067, -147.47648183, 211.8, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'demo-data/2021.january.27\\20210127T080320_radar.log'))

    testRange2 = (datetime.datetime(2021, 1, 27, 20, 33, 17, 150000), 28.325000762939453, 65.12908123766272, -147.4746841626404, 374.5324373104134, 327.42216601810213, 0.051963888108730316, 3.7164359092712402, 1.6885007619857788, 46.87992858886719, 26.992938995361328, 367.3486022949219, 'demo-data/2021.january.27\\20210127T081151_radar.log')
    sampleRange = []
    sampleRange.append((datetime.datetime(2021, 1, 27, 20, 3, 20, 88000), 0.0, 65.12624067, -147.47648183, 211.8, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'demo-data/2021.january.27\\20210127T080320_radar.log'))

    testTruth=(datetime.datetime(2021, 1, 27, 20, 43, 1), 65.1283760368824, -147.47867703437805, 407.74)

    is_fov = is_point_in_fov(testRange2, testTruth, useRangeAsTrue=True, generate_debug_graph=True)

    print(is_fov.is_in_fov)


if __name__ == "__main__":
    main()