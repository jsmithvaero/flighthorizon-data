"""
file    : runner.py
author  : Max von Hippel;
authored: 4 July 2021
usage   : python3 runner.py demo-data
"""
import sys
import argumentKeys as argKeys
import argparse

from src.radarData          import RadarData
from src.blocks             import radarTruthBlocks
from src.truthData          import *
from src.questions.Question import *

TRIVIAL_THRESHOLD = 4

INDEPENDENTS_to_run = range(0, len(INDEPENDENTS)-1, 1)
DEPENDENTS_to_run = range(0, len(DEPENDENTS)-1, 1)

def main():

    CLI=argparse.ArgumentParser()
    CLI.add_argument(
        argKeys.folder,
        nargs=1,
        type=str,
        default='demo-data/'
    )
    CLI.add_argument(
        argKeys.run_independents_key,
        nargs="*",
        type=int,
        default=INDEPENDENTS_to_run
    )
    CLI.add_argument(
        argKeys.run_dependents_key,
        nargs="*",
        type=int,
        default=DEPENDENTS_to_run
    )

    args = CLI.parse_args()

    # We begin by finding all of the data.
    input_folder = args.folder[0]

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
        if RD.isNonTrivial(TRIVIAL_THRESHOLD) and
        TD.isNonTrivial(TRIVIAL_THRESHOLD)
    ]

    # Finally, let's answer some questions, over the various blocks.
    for (RD, TD) in BLOCKED_DATAS:

        for (independent_parser, independent_name) in INDEPENDENTS:

        	timestamped_INDEPENDENT = independent_parser(RD, TD)

        	for (dependent_parser, dependent_name) in DEPENDENTS:

        		timestamped_DEPENDENT = dependent_parser(RD, TD)

        		answer = Question(
        			timestamped_X=timestamped_INDEPENDENT,
        			timestamped_Y=timestamped_DEPENDENT,
        			X_axis_name=independent_name,
        			Y_axis_name=dependent_name)

        		if answer.isNonTrivial():
	        		answer.plotXY(save=True)

    print("DONE")

if __name__ == "__main__":
    main()