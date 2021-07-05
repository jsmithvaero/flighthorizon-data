"""
file    : runner.py
author  : Max von Hippel;
authored: 4 July 2021
usage   : python3 runner.py demo-data
"""
import sys

from src.radarData import RadarData
from src.truthData import ADSBData,    \
                          NMEAData,    \
                          GPXData,     \
                          MavlinkData, \
                          TruthData
from src.blocks    import radarTruthBlocks

from src.questions.Question import Question

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

    # Finally, let's answer some questions, over the various blocks.
    for (RD, TD) in BLOCKED_DATAS:

    	print("TODO")


    print("DONE")

if __name__ == "__main__":
    main()