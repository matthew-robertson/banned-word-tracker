import unittest
from unittest.mock import patch 
import datetime

from utils.time import is_valid_time, parse_time, format_seconds, format_time

class TestIsValidTime(unittest.TestCase):
    def test_is_valid_time__valid_time(self):
        time_splits = ['0', '120']
        result = is_valid_time(time_splits)
        self.assertTrue(result)

        time_splits = ['12']
        result = is_valid_time(time_splits)
        self.assertTrue(result)

        time_splits = ['1', '69', '420']
        result = is_valid_time(time_splits)
        self.assertTrue(result)

    def test_is_valid_time__negative_time(self):
        time_splits = ['-12', '2']
        result = is_valid_time(time_splits)
        self.assertFalse(result)

    def test_is_valid_time__too_long(self):
        time_splits = ['1', '1', '1', '1']
        result = is_valid_time(time_splits)
        self.assertFalse(result)

    def test_is_valid_time__fractional_time(self):
        time_splits = ['1.2']
        result = is_valid_time(time_splits)
        self.assertFalse(result)

    def test_is_valid_time__letters(self):
        time_splits = ['asdf', 'fds']
        result = is_valid_time(time_splits)
        self.assertFalse(result)

class TestParseTime(unittest.TestCase):
    def test_parse_time__all_three(self):
        times = ['4', '10', '54']
        result = parse_time(':'.join(times))

        self.assertEqual(result, int(times[-1]) + 60 * int(times[-2]) + 60*60 * int(times[-3]))

    def test_parse_time__only_two(self):
        times = ['1230', '54']
        result = parse_time(':'.join(times))

        self.assertEqual(result, int(times[-1]) + 60 * int(times[-2]))

    def test_parse_time__only_seconds(self):
        times = ['88']
        result = parse_time(times[0])

        self.assertEqual(result, int(times[-1]))

        result = parse_time(times[0])
        self.assertEqual(result, int(times[-1]))

    def test_parse_time__too_many(self):
        times = ['4', '10', '5', '3']
        result = parse_time(':'.join(times))

        self.assertEqual(result, -1)

    def test_parse_time__wrong_separator(self):
        times = ['4', '10', '5']
        result = parse_time('!'.join(times))

        self.assertEqual(result, -1)

    def test_parse_time__bad_number(self):
        times = ['4', '10as', '5']
        result = parse_time(':'.join(times))

        self.assertEqual(result, -1)

class TestFormatSeconds(unittest.TestCase):
    def test_format_seconds__more_than_one_of_each(self):
        seconds = 7
        seconds += 45*60
        seconds += 3*60*60
        seconds += 6*60*60*24

        time = format_seconds(seconds)
        self.assertEqual(time, "6 days, 3 hours, 45 minutes, and 7 seconds")

    @patch('utils.time.format_time')
    def test_format_seconds__calls_underlying_function(self, mockClass):
        time = format_seconds(12356)
        self.assertTrue(mockClass.called)

class TestFormatTime(unittest.TestCase):
    def test_format_time__one_of_each_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 22, 7, 3)
        last_infraction_time = infraction_time - datetime.timedelta(days=1, hours=1, minutes=1, seconds=1)

        time = format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "1 day, 1 hour, 1 minute, and 1 second")

    def test_format_time__more_than_a_day_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 22, 7, 3)
        last_infraction_time = infraction_time - datetime.timedelta(days=1, minutes=42)

        time = format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "1 day, 42 minutes, and 0 seconds")

    def test_format_time__less_than_a_day_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 22, 7, 3)
        last_infraction_time = infraction_time - datetime.timedelta(hours=14, minutes=34, seconds=42)

        time = format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "14 hours, 34 minutes, and 42 seconds")

    def test_format_time__less_than_an_hour_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 6, 7, 3)
        last_infraction_time = infraction_time - datetime.timedelta(minutes=34, seconds=42)

        time = format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "34 minutes and 42 seconds")

    def test_format_time__less_than_a_minute_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 7, 31, 3)
        last_infraction_time = infraction_time - datetime.timedelta(seconds=42)

        time = format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "42 seconds")
