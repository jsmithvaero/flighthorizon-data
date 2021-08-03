"""
file    : TimeToDetect.py
author  : Levi Purdy
authored: 3 August 2021
purpose : To find information on how long it took an aircraft to be detected when entering a radar's FoV
"""

# Goal: Generate a list of time it took radar to detect, and a histogram from that list

# Steps:
# Get the approriate radar physical and fov information.

# Run the truth information through the fov test sequentially, and append a in or out

# Segment the transitions out --> in into an encounter datastructure

# Make a list of encounters

# Process the list of encounters to get a list of time to detect

