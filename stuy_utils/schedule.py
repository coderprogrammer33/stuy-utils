import csv
from collections import namedtuple
from datetime import date, timedelta
from datetime import datetime as dt
from datetime import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import requests
import warnings

from stuy_utils import errors

Info = namedtuple("Info", ("school", "cycle", "schedule", "testing", "events"))
Time = namedtuple("Time", ("start", "end"))

TERM_PATH = f"{Path(__file__).parent}/data/term-days.tsv"
REGULAR_BELLS_PATH = f"{Path(__file__).parent}/data/regular.tsv"
CONFERENCE_BELLS_PATH = f"{Path(__file__).parent}/data/conference.tsv"
HOMEROOM_BELLS_PATH = f"{Path(__file__).parent}/data/homeroom.tsv"
PTC_BELLS_PATH = f"{Path(__file__).parent}/data/ptc.tsv"
EXTENDED_HOMEROOM_BELLS_PATH = f"{Path(__file__).parent}/data/extended_homeroom.tsv"


def update_schedule():
    """Updates term-days.tsv.
    
    Makes sure that term-days.tsv is up-to-date by rewriting it with a guaranteed up-to-date version.
    
    No args, no raises, no return value.
    
    Warns if an exception is encountered when sending a request.
    """
    try:
        r = requests.get("https://docs.google.com/spreadsheets/d/16BQyzd2rp7UP2nj0wx1I7DvopDhm8sZ65-xSEqE1-5c/export?format=tsv&gid=1814525404")
    except requests.ConnectionError:
        warnings.warn("Schedule could not update due to a connection error.")
    except Exception as e:
        warnings.warn("Schedule could not update due to an exception: {e}")
    else:
        with open('text.tsv', 'wb') as f:
            f.write(r.content)


def convert_12h_to_24h(hours12: str) -> str:
    """Converts a 12-hour time to a 24-hour time.

    Converts a 12-hour time to a 24-hour time by adding 12 hours to the
    hour if the time is in the PM.

    Args:
        hours12: A string representing a 12-hour time.
        e.g "1:00 PM"

    Raises:
        errors.InvalidTime: Thrown if the input is not a string.
        errors.InvalidTime: Thrown if the input isn't a 12-hour time
        (i.e. doesn't contain AM or PM, or hours > 12).

    Returns:
        str: A string representing a 24-hour time, with 0 prepended
        to the front of the time if the hour is less than 10.
    """

    if not isinstance(hours12, str):
        raise errors.InvalidTime(hours12)

    if "AM" in hours12 or "PM" in hours12:
        hours12time = hours12.split(" ")[0]
        am_pm = hours12.split(" ")[1]
    else:
        raise errors.InvalidTime(hours12)

    if ":" not in hours12:
        raise errors.InvalidTime(hours12)

    hours, minutes = hours12time.split(":")

    if int(hours) > 12:
        raise errors.InvalidTime(hours12)

    # Account for 12:00 AM being 0 hours
    if hours == "12":
        hours = "0"
    if am_pm == "PM":
        hours = str(int(hours) + 12)

    if int(hours) < 10:
        hours = f"0{hours}"

    return f"{hours}:{minutes}"


def convert_24h_to_minutes(hours24: str) -> int:
    """Convert a 24-hour time to minutes.

    Converts a 24-hour time to minutes by converting the hours and minutes

    Args:
        hours24: A string representing a 24-hour time.
        e.g "13:00"

    Raises:
        errors.InvalidTime: Thrown if the input is not a string.
        errors.InvalidTime: Thrown if the input isn't a 24-hour time (i.e. doesn't contain :, or hours > 24).

    Returns:
        int: The number of minutes since midnight.
    """

    if not isinstance(hours24, str):
        raise errors.InvalidTime(hours24)

    if ":" not in hours24:
        raise errors.InvalidTime(hours24)

    hours, minutes = hours24.split(":")

    if int(hours) > 24:
        raise errors.InvalidTime(hours24)

    return int(hours) * 60 + int(minutes)


update_schedule()
with open(TERM_PATH, "r") as term_tsv, open(REGULAR_BELLS_PATH, "r") as regular_tsv, open(CONFERENCE_BELLS_PATH,
                                                                                          "r") as conference_tsv, open(
    HOMEROOM_BELLS_PATH, "r") as homeroom_tsv:
    TERM_DAYS = {row[0]: Info(*row[1:]) for row in list(csv.reader(term_tsv, delimiter="\t"))[1:]}
    REGULAR_BELL_SCHEDULE = {row[0]: Time(*[time.fromisoformat(convert_12h_to_24h(element)) for element in row[1:]]) for
                             row in
                             list(csv.reader(regular_tsv, delimiter="\t"))[1:]}
    CONFERENCE_BELL_SCHEDULE = {row[0]: Time(*[time.fromisoformat(convert_12h_to_24h(element)) for element in row[1:]])
                                for row in
                                list(csv.reader(conference_tsv, delimiter="\t"))[1:]}
    HOMEROOM_BELL_SCHEDULE = {row[0]: Time(*[time.fromisoformat(convert_12h_to_24h(element)) for element in row[1:]])
                              for row in
                              list(csv.reader(homeroom_tsv, delimiter="\t"))[1:]}
    PTC_BELL_SCHEDULE = {row[0]: Time(*[time.fromisoformat(convert_12h_to_24h(element)) for element in row[1:]]) for row
                         in
                         list(csv.reader(homeroom_tsv, delimiter="\t"))[1:]}
    EXTENDED_HOMEROOM_BELL_SCHEDULE = {
        row[0]: Time(*[time.fromisoformat(convert_12h_to_24h(element)) for element in row[1:]]) for row in
        list(csv.reader(homeroom_tsv, delimiter="\t"))[1:]}


def convert_to_isoformat(day: Union[date, dt]) -> str:
    """Convert a date object to an ISO-formatted date string.

    Convert a date or datetime object from the datetime library to a string
    formatted using the ISO 8601 format, while also checking if 'date' is a
    valid date and if it exists in the data.

    Args:
        day (Union[datetime.date, datetime.datetime]): A date or datetime
        object from the datetime library.

    Raises:
        errors.InvalidDate: Thrown if the input is not a date or a datetime
        object.
        errors.DayNotInData: Thrown if the inputted day is not in
        term_days.csv.

    Returns:
        str: A date using the ISO 8601 format (yyyy-mm-dd).
    """
    if not isinstance(day, date):
        raise errors.InvalidDate(day)

    if isinstance(day, dt):
        day = day.date()  # Converts datetime to date to remove time

    iso_date = day.isoformat()

    # if this code is not commented out, it will throw errors since TERM_DAYS is nonexistent.
    """
    if iso_date not in TERM_DAYS:
        raise errors.DayNotInData(iso_date)
    """

    return iso_date


def get_day_info(day: Union[date, dt]) -> Info:
    """Returns information about a given day.

    Returns the cycle, period, testing subjects, and any events of a given
    day. If a category does not apply, a value of None is returned.

    Args:
        day (Union[datetime.date, datetime.datetime]): A date or datetime
        object from the datetime library.

    Raises:
        errors.InvalidDate: Thrown if the input is not a date or a datetime
        object.
        errors.DayNotInData: Thrown if the inputted day is not in
        term_days.csv.

    Returns:
        Info: A namedtuple with fields 'school', 'cycle', 'schedule', 'testing', and 'events'.
    """

    if not isinstance(day, date):
        raise errors.InvalidDate(day)

    if isinstance(day, dt):
        day = day.date()  # Converts datetime to date to remove time

    iso_date = day.isoformat()

    if iso_date not in TERM_DAYS:
        raise errors.DayNotInData(iso_date)

    ret_tuple = Info(school=True if TERM_DAYS[iso_date][0] == "True" else False,
                     cycle=TERM_DAYS[iso_date][1] if TERM_DAYS[iso_date][1] != "None" else None,
                     schedule=TERM_DAYS[iso_date][2] if TERM_DAYS[iso_date][2] != "None" else None,
                     testing=TERM_DAYS[iso_date][3] if TERM_DAYS[iso_date][3] != "None" else None,
                     events=TERM_DAYS[iso_date][4] if TERM_DAYS[iso_date][4] != "None" else None, )

    return ret_tuple


def get_next_school_day(day: Union[date, dt], always_same: bool = False) -> Optional[date]:
    """Returns when the next school day is.

    Returns a date object of the next school day from the given day. The given
    datetime will be returned as a date if school is still in session.

    Args:
        day (Union[datetime.date, datetime.datetime]): A date or datetime
        object from the datetime library.
        always_same (bool, optional): Whether to always return the given
        day if the given day is a school day. Defaults to False.

    Raises:
        errors.InvalidDate: Thrown if the input is not a datetime object.
        errors.DayNotInData: Thrown if the inputted day is not in
        term_days.csv.

    Returns:
        Optional[datetime.date]: A date object with the year, month, and day
        of the next school day.
    """

    if not isinstance(day, date):
        raise errors.InvalidDate(day)

    if isinstance(day, dt):
        day = day.date()  # Converts datetime to date to remove time

    iso_date = day.isoformat()

    if iso_date not in TERM_DAYS:
        raise errors.DayNotInData(iso_date)

    if TERM_DAYS[iso_date][0] == "True":
        return day

    if always_same:
        return day

    next_day = day + timedelta(days=1)
    while get_day_info(next_day).school is False:
        if next_day.isoformat() not in TERM_DAYS:
            return None
        next_day = next_day + timedelta(days=1)

    return next_day


def get_bell_schedule(day: Union[date, dt], this_day: bool = False) -> Optional[dict]:
    """Returns the bell periods of the next school day.

    Returns a dictionary of bell periods of the next school day. If the given
    day is a school day, then the bell schedule of that day will be returned,
    even if it is after-school. ⬅️!?!

    Args:
        this_day: Whether to return the bell schedule of the given
        day (Union[datetime.date, datetime.datetime]): A date or datetime
        object from the datetime library.

    Raises:
        errors.InvalidDate: Thrown if the input is not a datetime object.
        errors.DayNotInData: Thrown if the inputted day is not in
        term_days.csv.

    Returns:
        Dict[str, Time]: A dictionary of keys of strings of the category name
        (see data/bell_schedule.csv) and values of Time namedtuple objects with
        fields 'start' and 'end', which returns a datetime object.
    """

    if not isinstance(day, date):
        raise errors.InvalidDate(day)

    if isinstance(day, dt):
        day = day.date()  # Converts datetime to date to remove time

    iso_date = day.isoformat()

    if iso_date not in TERM_DAYS:
        raise errors.DayNotInData(iso_date)

    if TERM_DAYS[iso_date][0] == "True":
        if TERM_DAYS[iso_date][2] == "None":
            # should never happen, but return regular bell schedule if it does
            return None
        else:
            if TERM_DAYS[iso_date][2] == "Regular":
                return REGULAR_BELL_SCHEDULE
            elif TERM_DAYS[iso_date][2] == "Conference":
                return CONFERENCE_BELL_SCHEDULE
            elif TERM_DAYS[iso_date][2] == "Homeroom":
                return HOMEROOM_BELL_SCHEDULE
            elif TERM_DAYS[iso_date][2] == "PTC":
                return PTC_BELL_SCHEDULE
            elif TERM_DAYS[iso_date][2] == "Extended Homeroom":
                return EXTENDED_HOMEROOM_BELL_SCHEDULE
            else:
                return None

    else:
        if this_day:
            return None
        else:
            # next day, use get_next_school_day
            next_day = get_next_school_day(day)
            return get_bell_schedule(next_day)


def get_current_class(day: dt) -> Optional[Tuple[str, Time]]:
    """Returns information of the current class.

    Returns a tuple of information of the current class, where the first
    element is a string of the category, such as the class period, and a Time
    namedtuple object, which includes when said period starts and ends.

    Args:
        day (datetime.datetime): A datetime object from the datetime library.

    Raises:
        errors.InvalidDate: Thrown if the input is not a datetime object.
        errors.DayNotInData: Thrown if the inputted day is not in
        term_days.csv.

    Returns:
        Optional[Tuple[str, Time]]: A tuple of a string of the category name
        (see data/bell_schedule.csv), and a Time namedtuple object with fields
        'start' and 'end', which returns a datetime object.
    """
    schedule = get_bell_schedule(day)

    day = day.time()

    for item in schedule.items():
        if item[1].start <= day <= item[1].end:
            return item

    return None


def get_next_class(day: dt, skip_passing: bool = False) -> Optional[Tuple[str, Time]]:
    """Returns information of the next class.

    Returns a tuple of information of the next class, where the first element
    is a string of the category, such as the class period, and a Time
    namedtuple object, which includes when said period starts and ends.

    Args:
        skip_passing: Whether to skip passing periods.
        day (datetime.datetime): A datetime object from the datetime library.

    Raises:
        errors.InvalidDate: Thrown if the input is not a datetime object.
        errors.DayNotInData: Thrown if the inputted day is not in
        term_days.csv.

    Returns:
        Optional[Tuple[str, Time]]: A tuple of a string of the category name
        (see data/bell_schedule.csv), and a Time namedtuple object with fields
        'start' and 'end', which returns a datetime object.
    """

    schedule = get_bell_schedule(day)

    current_class = get_current_class(day)

    if current_class is None:
        return next(iter(schedule.items()))

    else:
        # Find index of current class
        index = list(schedule.keys()).index(current_class[0])

        # If the current class is the last class, return None
        if index == len(schedule.keys()) - 1:
            return None

        # Otherwise, find the next class
        else:
            next_class = list(schedule.keys())[index + 1]
            # If next class name contains "Passing", skip it
            if skip_passing and "Passing" in next_class:
                next_class = list(schedule.keys())[index + 2]
            else:
                return next_class, schedule[next_class]

            return next_class, schedule[next_class]


def get_current_period(time_of_period: dt) -> Optional[str]:
    """Returns the current period.

    Returns the current period, where the first element is a string of the
    category, such as the class period, and a Time namedtuple object, which
    includes when said period starts and ends.

    Args:
        time_of_period (datetime.datetime): A datetime object from the datetime library.

    Raises:
        errors.InvalidDate: Thrown if the input is not a datetime object.
        errors.DayNotInData: Thrown if the inputted day is not in
        term_days.csv.

    Returns:
        Optional[str]: A string of the category name (see data/bell_schedule.csv)
    """

    current_class = get_current_class(time_of_period)

    if current_class is None:
        return None

    else:
        return current_class[0]
