"""
__author__ = "Alexander Sahm"
__copyright__ = "Copyright 2020, Pomfort GmbH"

__license__ = "MIT"
__maintainer__ = "Patrick Renner, Alexander Sahm"
__email__ = "opensource@pomfort.com"
"""

import datetime
import os
import time


def matches_prefixes(text: str, prefixes: list):
    for prefix in prefixes:
        if text.startswith(prefix):
            return True
    return False


def datetime_isostring(date, keep_microseconds=False):
    """create an iso string representation for a date object
    e.g. for use in XML tags and attributes

    arguments:
    date -- date object
    keep_microseconds -- include microseconds in iso
    """
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)

    if keep_microseconds:
        date_to_format = date
    else:
        date_to_format = date.replace(microsecond=0)

    return date_to_format.replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


def datetime_now_isostring():
    return datetime_isostring(datetime.datetime.now())


def datetime_now_filename_string():
    """create a string representation for now() for use as part of the MHL filename"""
    return datetime.datetime.strftime(datetime.datetime.now(datetime.UTC), "%Y-%m-%d_%H%M%SZ")


def datetime_now_isostring_with_microseconds():
    return datetime_isostring(datetime.datetime.now(), keep_microseconds=True)


def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n] + "B"


def get_case_sensitive_file_names_in_folder(root):
    result = []
    for dir_path, dir_names, file_names in os.walk(root):
        result.extend([os.path.join(dir_path, file_name) for file_name in file_names])
        result.extend([os.path.join(dir_path, dir_name) for dir_name in dir_names])
    return result
