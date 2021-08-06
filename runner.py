"""
file    : runner.py
author  : Max von Hippel;
authored: 4 July 2021
usage   : python3 runner.py demo-data
"""
import sys
import argumentKeys as argKeys

from src.radarData          import RadarData
from src.blocks             import radarTruthBlocks
from src.truthData          import *
from src.questions.Question import *
from src.questions.TimeToDetect import *

TRIVIAL_THRESHOLD = 4

def main():

    args = argKeys.parse()

    # We begin by finding all of the data.
    input_folder = args.folder[0]

    radarD = RadarData  (input_folder)
    if args.noadsb:
        nmeaD = NMEAData(input_folder)
        gpxD = GPXData(input_folder)
        mavlD = MavlinkData(input_folder)

        truthD = gpxD.union(nmeaD) \
                     .union(mavlD)
    elif args.nogpx:
        adsbD = ADSBData(input_folder)
        nmeaD = NMEAData(input_folder)
        mavlD = MavlinkData(input_folder)

        truthD = adsbD.union(nmeaD) \
            .union(mavlD)
    else:
        adsbD  = ADSBData   (input_folder)
        nmeaD  = NMEAData   (input_folder)
        gpxD   = GPXData    (input_folder)
        mavlD  = MavlinkData(input_folder)

        truthD = adsbD.union(nmeaD)\
                      .union(gpxD)\
                      .union(mavlD)

    print(truthD.quickStats())

    # TODO: Add code that makes sure truth data from different sources ends up in different data blocks in BLOCKED_DATA
    # TODO: Add code that makes sure radar data from different radars ends up in different data blocks

    # Now that we have truth and radar, let's bin it up into blocks.
    BLOCKS = radarTruthBlocks(radarD.getPoints(), truthD.getPoints())

    BLOCKED_DATAS = [
        (RadarData(folder=None, points=radarBlock),
         TruthData(folder=None, points=truthBlock))
        
        for (radarBlock, truthBlock) in BLOCKS
    ]

    # Remove singletons and empty sets.
    BLOCKED_DATAS = [
        
        (RD, TD) for (RD, TD) in BLOCKED_DATAS
        
        if RD.isNonTrivial(TRIVIAL_THRESHOLD) and
           TD.isNonTrivial(TRIVIAL_THRESHOLD)
    ]

    if args.ttd:
        # For every
        for (RD, TD) in BLOCKED_DATAS:
            answer = TimeToDetect(RD, TD)
            print(answer.time_to_detect)
        pass


    # Finally, let's answer some questions, over the various blocks.
    for (RD, TD) in BLOCKED_DATAS:


        for countI, (independent_parser, independent_name) in enumerate(INDEPENDENTS):

            for countD, (dependent_parser, dependent_name) in enumerate(DEPENDENTS):

                if countI in args.independents and countD in args.dependents:

                    timestamped_INDEPENDENT = independent_parser(RD, TD)
                    timestamped_DEPENDENT   = dependent_parser(RD, TD)

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