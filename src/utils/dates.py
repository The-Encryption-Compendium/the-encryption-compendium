"""
Various utilities for handling dates and times.
"""

import calendar
import datetime


def months():
    """
    Return a list of all of the months of the year.
    """
    return [
        datetime.date(year=1900, month=ii, day=1).strftime("%B") for ii in range(1, 13)
    ]


def month_name(month_num: int):
    """
    Get the name of a month corresponding to its number (1 to 12).
    Returns None if the input number is invalid.
    """
    try:
        date = datetime.date(year=1900, month=month_num, day=1)
        return date.strftime("%B")
    except:
        return None


def month_num(month_name: str):
    """
    Get the number of a month (1 to 12) corresponding to its name.
    Returns None if the input name is invalid.
    """

    for (num, name) in enumerate(calendar.month_name):
        if name == month_name:
            return num

    return None
