"""
file    : Encounter.py
author  : Levi Purdy
authored: 4 August 2021
purpose : A class that holds information associated with an encounter
"""

class Encounter():
    def __init__(self, encounter_TD_point,
                 encounter_RD_sequence,
                 encounter_TD_sequence = None,
                 ):
        self.encounter_TD_sequence = encounter_TD_sequence if encounter_TD_sequence is not None else encounter_TD_point
        self.encounter_TD_point = encounter_TD_point
        self.encounter_RD_sequence = encounter_RD_sequence
