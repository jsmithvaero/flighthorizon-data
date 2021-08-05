"""
file    : TimeToDetect.py
author  : Levi Purdy
authored: 3 August 2021
purpose : To find information on how long it took an aircraft to be detected when entering a radar's FoV
"""
from src.questions.Question import Question
from src.radarData import *
from src.Encounter import *

from datetime    import datetime
from datetime    import timedelta


# Goal: Generate a list of time it took radar to detect, and a histogram from that list

# Possibly build RD TD as a parser that is also a question with its own graphs it can generate

class TimeToDetect(Question):

    def __init__ (self,
                  RD,
                  TD,
                  encounter_RD_grab_range=timedelta(seconds=60),
                  encounter_TD_grab_range=timedelta(seconds=60)
                  ):

        self.RD_ = RD
        self.TD_ = TD
        self.RD_source_ , self.TD_source_ = self.check_RD_TD_sources()
        if len(self.RD_source_) > 1 or len(self.TD_source_) > 1:
            print("TimeToDetect only setup for 1 radar source and 1 aircraft truth source. Please split when blocking.")
            assert(False)
        self.RD_source_ = self.RD_source_[0]
        self.TD_source_ = self.TD_source_[0]
        self.RD_physical_ = self.get_radar_physical_()
        self.RD_fov_ = self.get_radar_fov_()
        self.encounter_RD_grab_range = encounter_RD_grab_range
        self.encounter_TD_grab_range = encounter_TD_grab_range
        self.encounter_list = []


# Steps:
    # Check to make sure source data is only 1 radar 1 plane
    def check_RD_TD_sources(self):
        RD_sources = []
        TD_sources = []
        for point in self.RD_:
            if point.src not in RD_sources:
                RD_sources.append(point.src)
        for point in self.TD_:
            if point.src not in TD_sources:
                TD_sources.append(point.src)
        return RD_sources, TD_sources

# Get the approriate radar physical and fov information.
    def get_radar_physical_(self):
        return get_radar_physical(self.RD_source_)
    def get_radar_fov_(self):
        return get_radar_fov(self.RD_source_)
# Run the truth information through the fov test sequentially, and append a in or out
    def classify_in_fov(self):
        for id, tpoint in enumerate(self.TD_):
            fov_check = is_point_in_fov(self.RD_[0],
                                        tpoint,
                                        fov=self.RD_fov_,
                                        physical=self.RD_physical_)
            self.TD_[id].fov_test = fov_check
# Segment the transitions out --> in into an encounter datastructure
    # Make a list of encounters
    def populate_encounter_list(self):
        # setup
        last_in_FoV = False
        # iterate through truth point list
        for id, tpoint in enumerate(self.TD_):
            # if last_in_FoV is False, and tpoint.fov_test.is_in_fov is True
            if last_in_FoV is False and tpoint.fov_test.is_in_fov:
                # set last_in_Fov to True
                last_in_FoV = True
                # Begin encounter construction:
                encounter_time = tpoint.stamp
                    # Find truth data around the encounter point
                nearby_truths = self.list_points_within_timerange(self.TD_,
                                                                  encounter_time,
                                                                  self.encounter_TD_grab_range)
                    # Find radar data around the encounter point
                nearby_radar_points = self.list_points_within_timerange(self.RD_,
                                                                        encounter_time,
                                                                        self.encounter_RD_grab_range)
                    # Construct an encounter and append it to the encounter list
                encounter = Encounter(tpoint, nearby_radar_points, nearby_truths)
                self.encounter_list.append(encounter)
            # elseif last_in_FoV is True and tpoint.fov_test.is_in_fov is False
            elif last_in_FoV and tpoint.fov_test.is_in_fov is False:
                # set last_in_FoV to False
                last_in_FoV = False
            # else do nothing, because it is just outside of the FoV, or still inside the FoV
            else:
                pass



# Process the list of encounters to get a list of time to detect


# Useful functions
    def list_points_within_timerange(self, points, target_time, time_delta):
        valid_points = []
        for point in points:
            if abs(point.stamp-target_time) < time_delta:
                valid_points.append(point)
        return valid_points