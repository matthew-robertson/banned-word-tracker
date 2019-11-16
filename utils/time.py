import math
import datetime

def parse_time(time_string):
    splits = time_string.strip().split(':')
    if not is_valid_time(splits):
        return -1

    second_total = int(splits[-1])
    if len(splits) >= 2:
        second_total += int(splits[-2]) * 60
    if len(splits) >= 3:
        second_total += int(splits[-3]) * 60 * 60

    return second_total

def is_valid_time(time_splits):
    return all(split.isnumeric() for split in time_splits) and len(time_splits) <= 3

def format_seconds(seconds_count):
    current_time = datetime.datetime.now()
    return format_time(current_time, current_time - datetime.timedelta(seconds=seconds_count))

def format_time(current_time, pastTime):
    diff = current_time - pastTime
    hours = math.floor(diff.seconds/3600)
    minutes = math.floor((diff.seconds - hours*3600)/60)
    seconds = diff.seconds - hours*3600 - minutes*60
    dt = "{} days, ".format(diff.days)
    ht = "{} hours, ".format(hours)
    mt = "{} minutes, and ".format(minutes)
    st = "{} seconds".format(seconds)

    if diff.days == 1:
        dt = "1 day, "
    elif diff.days == 0:
        dt = ""
        if hours == 0:
            ht = ""
            mt = "{} minutes and ".format(minutes)
            if minutes == 0:
                mt = ""

    if hours == 1:
        ht = "1 hour, "
    elif hours == 0:
        ht = ""

    if minutes == 1:
        if ht == "":
            mt = "1 minute and "
        else:
            mt = "1 minute, and "

    if seconds == 1:
        st = "1 second"

    return dt+ht+mt+st