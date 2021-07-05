"""
file    : runner.py
author  : Max von Hippel;
authored: 4 July 2021
usage   : python3 runner.py demo-data
"""
import sys

from src.radarData          import RadarData
from src.blocks             import radarTruthBlocks
from src.truthData          import *
from src.questions.Question import *

def main():
    if len(sys.argv) < 2:
        print("Error - missing required argument for data dir.")
        return

    # We begin by finding all of the data.
    input_folder = sys.argv[1]

    radarD = RadarData  (input_folder)
    
    adsbD  = ADSBData   (input_folder)
    nmeaD  = NMEAData   (input_folder)
    gpxD   = GPXData    (input_folder)
    mavlD  = MavlinkData(input_folder)

    truthD = adsbD.union(nmeaD)\
                  .union(gpxD)\
                  .union(mavlD)

    print(truthD.quickStats())

    # Now that we have truth and radar, let's bin it up into blocks.
    BLOCKS = radarTruthBlocks(radarD.getPoints(), truthD.getPoints())

    BLOCKED_DATAS = [
    	(RadarData(folder=None,points=radarBlock),
    	 TruthData(folder=None,points=truthBlock))
    	for (radarBlock, truthBlock)
    	in BLOCKS
    ]

    # Remove singletons and empty sets.
    BLOCKED_DATAS = [
    	(RD, TD) for (RD, TD) in BLOCKED_DATAS
        if RD.isNonTrivial() and
        TD.isNonTrivial()
    ]

    # Finally, let's answer some questions, over the various blocks.
    for (RD, TD) in BLOCKED_DATAS:

        # 1. How does distance from the RADAR impact ...
        distances_from_RADAR = distanceFromRadarParser(RD)
        # (3) reported confidence of the RADAR data?
        reported_confidences = confidencesOfRadar(RD)

        one_dot_three = Question(timestamped_X=distances_from_RADAR,
        	                     timestamped_Y=reported_confidences,
        	                     X_axis_name="Distance from RADAR (m)",
        	                     Y_axis_name="Reported RADAR confidence (%)")
        one_dot_three.plotXY()



    print("DONE")

if __name__ == "__main__":
    main()