"""
file    : argumentKeys.py
author  : Levi Purdy;
authored: 7/15/2021
usage   : library of variables for runner.py
"""
import argparse
from src.questions.Question import *


folder_key = '-folder'
run_dependents_key = '--dependents'
run_independents_key = '--independents'
run_time_to_detection_key = '-ttd'

INDEPENDENTS_to_run = range(0, len(INDEPENDENTS)-1, 1)
DEPENDENTS_to_run = range(0, len(DEPENDENTS)-1, 1)

CLI = argparse.ArgumentParser()

def parse():
    # Arguments can be added here
    CLI.add_argument(
        folder_key,
        nargs=1,
        type=str,
        default='demo-data/'
    )
    CLI.add_argument(
        run_independents_key,
        nargs="*",
        type=int,
        default=INDEPENDENTS_to_run
    )
    CLI.add_argument(
        run_dependents_key,
        nargs="*",
        type=int,
        default=DEPENDENTS_to_run
    )
    CLI.add_argument(
        run_time_to_detection_key,
        action='store_true'
    )

    return CLI.parse_args()




