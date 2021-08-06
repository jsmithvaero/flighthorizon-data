"""
file    : Encounter.py
author  : Levi Purdy
authored: 4 August 2021
purpose : A class that holds information associated with an encounter
"""
from src.mathUtils import PAC
from datetime import timedelta

class Encounter():
    def __init__(self, TD_point,
                 RD_sequence,
                 TD_sequence = None,
                 ):
        self.TD_sequence = TD_sequence if TD_sequence is not None else TD_point
        self.TD_point = TD_point
        self.RD_sequence = RD_sequence
        self.first_valid_RD_point_location = None
        self.RD_passed_PAC = []
        self.PAC_hoz_deviation = 100 # meters
        self.PAC_vert_deviation = 100 # meters
        self.PAC_time_deviation = 60 # seconds

    # Appends a PAC_results_TD_point to evey point in RD_sequence
    # This might need to be an asymetric test
    def append_TD_point_PAC_test(self):
        for id, RD_point in enumerate(self.RD_sequence):
            self.RD_sequence[id].PAC_results_TD_point = PAC(RD_point.stamp,
                                                   RD_point.latitude,
                                                   RD_point.longitude,
                                                   RD_point.altitude,
                                                   [self.TD_point],
                                                   allowed_hoz_deviation=self.PAC_hoz_deviation,
                                                   allowed_vertical_deviation=self.PAC_vert_deviation,
                                                   allowed_time_deviation=self.PAC_time_deviation
                                                   )


    def append_general_PAC_test(self):
        for id, RD_point in enumerate(self.RD_sequence):
            self.RD_sequence[id].PAC_results = PAC(RD_point.stamp,
                                                   RD_point.latitude,
                                                   RD_point.longitude,
                                                   RD_point.altitude,
                                                   self.TD_sequence,
                                                   allowed_hoz_deviation=self.PAC_hoz_deviation,
                                                   allowed_vertical_deviation=self.PAC_vert_deviation,
                                                   allowed_time_deviation=self.PAC_time_deviation
                                                   )

    def process_RD_passed_PAC(self):
        self.append_TD_point_PAC_test()
        # run through RD_sequence and find the first point that passed PAC_results
        min_time = None
        RD_passed_PAC = []
        for id, RD_point in enumerate(self.RD_sequence):
            # test if PAC_results is True
            if RD_point.PAC_results:
                # test if this is the earliest time PAC_results is true
                # choosing to use abs here, be aware that this depneds on PAC not allowing RD_points before
                # TD_point to be valid
                time_diff = abs(RD_point.stamp - self.TD_point.stamp)
                if min_time is None or time_diff < min_time:
                    min_time = time_diff
                    self.first_valid_RD_point_location = id
                    RD_point.time_diff = time_diff
                    self.RD_sequence[id].time_diff = time_diff
                RD_passed_PAC.append(RD_point)
        self.RD_passed_PAC = RD_passed_PAC



