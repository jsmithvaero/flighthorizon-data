"""
file    : runner.py
author  : Max von Hippel;PP
authored: 4 July 2021
usage   : python3 runner.py demo-data
"""
import sys
import argumentKeys as argKeys

from src.radarData               import RadarData
from src.radarDataGroundAware    import RadarDataGroundAware
from src.blocks                  import radarTruthBlocks
from src.truthData               import *
from src.questions.Question      import *
from src.questions.QuestionPcts  import *

TRIVIAL_THRESHOLD = 4


def main():

    args = argKeys.parse()
    argKeyList = list(vars(args).keys())

    # We begin by finding all of the data.
    input_folder = args.folder[0]

    radarD = RadarData(input_folder)
    adsbD = ADSBData(input_folder)
    nmeaD = NMEAData(input_folder)
    gpxD = GPXData(input_folder)
    mavlD = MavlinkData(input_folder)

    truthD = adsbD.union(nmeaD)\
                  .union(gpxD)\
                  .union(mavlD)

    # Answer any percent questions
    if "percents" in argKeyList:

        # for GroundAware
        radarDGA = RadarDataGroundAware(input_folder)
        questionPcts = QuestionPcts()
        questionPcts.invalidvsValidTracksGroundAware(radarDGA)
        questionPcts.radarAccuracyByDistanceAltitudeGroundAware(
            mavlD, radarDGA)

        # for Echodyne
        questionPcts.invalidvsValidTracks(radarD)
        questionPcts.radarAccuracyByDistanceAltitude(mavlD, radarD)

    print(truthD.quickStats())

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

    # Finally, let's answer some questions, over the various blocks.
    for (RD, TD) in BLOCKED_DATAS:
        for countI, (independent_parser, independent_name) in enumerate(INDEPENDENTS):
            for countD, (dependent_parser, dependent_name) in enumerate(DEPENDENTS):
                if countI in args.independents and countD in args.dependents:

                    timestamped_INDEPENDENT = independent_parser(RD, TD)
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
