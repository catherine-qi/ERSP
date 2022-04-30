"""
Some util functions.
Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import json
import time


def current_time_in_milliseconds():
    """
    A method that returns the current time in milliseconds.
    Returns:
        An int representing the current time in milliseconds.
    """
    return int(round(time.time() * 1000))