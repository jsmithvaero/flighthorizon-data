"""
file    : runner.py
author  : Max von Hippel;
authored: 4 July 2021
usage   : python3 runner.py demo-data
"""
import sys

from src.radarData import RadarData
from src.truthData import ADSBData, NMEAData, GPXData, MavlinkData

def main():
    input_folder = sys.argv[1]

    radarD = RadarData  (input_folder)
    adsbD  = ADSBData   (input_folder)
    nmeaD  = NMEAData   (input_folder)
    gpxD   = GPXData    (input_folder)
    mavlD  = MavlinkData(input_folder)

    print(radarD.quickStats())
    print(adsbD.quickStats())
    print(nmeaD.quickStats())
    print(gpxD.quickStats())
    print(mavlD.quickStats())



if __name__ == "__main__":
    main()