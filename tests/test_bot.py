import unittest
import datetime
from unittest.mock import Mock, patch

import bot

class TestAwakeNoCooldownBot(unittest.TestCase):
    def setUp(self):
        self.current_time = datetime.datetime.now()
        self.current_server = {
            'server_id' : 1,
            'awake' : True,
            'timeout_duration_seconds': 1800
        }
        self.banned_words = [{
            'rowid': 1,
            'server_id': 1,
            'banned_word': 'vore',
            'infracted_at': self.current_time - datetime.timedelta(minutes=30),
            'calledout_at': self.current_time - datetime.timedelta(minutes=30)
        },
        {
            'rowid': 2,
            'server_id': 2,
            'banned_word': 'bepis',
            'infracted_at': self.current_time - datetime.timedelta(minutes=30),
            'calledout_at': self.current_time - datetime.timedelta(minutes=30)
        }]
        self.server_dao = Mock(**{
            'get_server.return_value': self.current_server,
            'get_banned_words_for_server.return_value': self.banned_words,
            'insert_server.return_value': None
        })
        self.infringedString = "@test referenced a forbidden word, setting its counter back to 0.\n"
        self.infringedString += "I'll wait 30 minutes and 0 seconds before warning you for this word again.\n"
        self.infringedString += "The server went 30 minutes and 0 seconds without mentioning the forbidden word 'vore'."

    def test_handle_message__different_word(self):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "bepis is good",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message_to_send = bot.handle_message(self.server_dao, message, 1, self.current_time)

        infringedString = "@test referenced a forbidden word, setting its counter back to 0.\n"
        infringedString += "I'll wait 30 minutes and 0 seconds before warning you for this word again.\n"
        infringedString += "The server went 30 minutes and 0 seconds without mentioning the forbidden word 'bepis'."
        self.assertEqual(message_to_send, infringedString)

    def test_handle_message__valid_post(self):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "I am a good boy",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message_to_send = bot.handle_message(self.server_dao, message, 1, self.current_time)
        self.assertFalse(message_to_send)

    def test_handle_message__infringing_post_only(self):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "vore",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message_to_send = bot.handle_message(self.server_dao, message, 1, self.current_time)
        self.assertEqual(message_to_send, self.infringedString)

    def test_handle_message__infringing_post_embedded(self):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "asdf vore is the worst ",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message_to_send = bot.handle_message(self.server_dao, message, 1, self.current_time)
        self.assertEqual(message_to_send, self.infringedString)

    def test_handle_message__infringing_post_from_bot(self):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "asdf vore is the worst ",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': True
            }),
        })

        message_to_send = bot.handle_message(self.server_dao, message, 1, self.current_time)
        self.assertFalse(message_to_send)

    def test_handle_message__infringing_post_embedded_hyphen(self):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "asdf-vore-is the worst ",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message_to_send = bot.handle_message(self.server_dao, message, 1, self.current_time)
        self.assertEqual(message_to_send, self.infringedString)

    def test_handle_message__infringing_post_formatting(self):
        message1 = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "-v-o-r-e-",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message2 = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "**v**o**r**e**",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message3 = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "|||v||||o||||r||e|||",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message_to_send1 = bot.handle_message(self.server_dao, message1, 1, self.current_time)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send2 = bot.handle_message(self.server_dao, message2, 1, self.current_time)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send3 = bot.handle_message(self.server_dao, message3, 1, self.current_time)
        self.assertEqual(message_to_send1, self.infringedString)

    def test_handle_message__infringing_post_unicode(self):
        message1 = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "vÒrË",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message2 = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "vᴑRè",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message3 = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "vÓrËD",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message_to_send1 = bot.handle_message(self.server_dao, message1, 1, self.current_time)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send2 = bot.handle_message(self.server_dao, message2, 1, self.current_time)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send3 = bot.handle_message(self.server_dao, message3, 1, self.current_time)
        self.assertEqual(message_to_send1, self.infringedString)

class TestAwakeCooldownBot(unittest.TestCase):
    def setUp(self):
        self.current_time = datetime.datetime.now()
        self.current_server = {
            'server_id' : 1,
            'awake' : True,
            'timeout_duration_seconds': 1800
        }
        self.banned_words = [{
            'rowid': 1,
            'server_id': 1,
            'banned_word': 'vore',
            'infracted_at': self.current_time - datetime.timedelta(minutes=30),
            'calledout_at': self.current_time - datetime.timedelta(minutes=20)
        }]
        self.server_dao = Mock(**{
            'get_server.return_value': self.current_server,
            'get_banned_words_for_server.return_value': self.banned_words,
            'insert_server.return_value': None
        })
    def test_handle_message__infringing_post(self):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "vore",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })
        message_to_send = bot.handle_message(self.server_dao, message, 1, self.current_time)

        self.assertEqual(message_to_send, '')

class TestAsleepBot(unittest.TestCase):
    def setUp(self):
        self.current_time = datetime.datetime.now()
        self.current_server = {
            'server_id' : 1,
            'infracted_at': self.current_time - datetime.timedelta(minutes=30),
            'calledout_at': self.current_time - datetime.timedelta(minutes=40),
            'awake' : False,
            'timeout_duration_seconds': 1800
        }
        self.banned_words = [{
            'rowid': 1,
            'server_id': 1,
            'banned_word': 'vore',
            'infracted_at': self.current_time - datetime.timedelta(minutes=30),
            'calledout_at': self.current_time - datetime.timedelta(minutes=30)
        }]
        self.server_dao = Mock(**{
            'get_server.return_value': self.current_server,
            'get_banned_words_for_server.return_value': self.banned_words,
            'insert_server.return_value': None
        })
    def test_handle_message__infringing_post(self):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "vore",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })
        message_to_send = bot.handle_message(self.server_dao, message, 1, self.current_time)

        self.assertEqual(message_to_send, '')

class TestIsValidTime(unittest.TestCase):
    def test_is_valid_time__valid_time(self):
        time_splits = ['0', '120']
        result = bot.is_valid_time(time_splits)
        self.assertTrue(result)

        time_splits = ['12']
        result = bot.is_valid_time(time_splits)
        self.assertTrue(result)

        time_splits = ['1', '69', '420']
        result = bot.is_valid_time(time_splits)
        self.assertTrue(result)


    def test_is_valid_time__negative_time(self):
        time_splits = ['-12', '2']
        result = bot.is_valid_time(time_splits)
        self.assertFalse(result)

    def test_is_valid_time__too_long(self):
        time_splits = ['1', '1', '1', '1']
        result = bot.is_valid_time(time_splits)
        self.assertFalse(result)

    def test_is_valid_time__fractional_time(self):
        time_splits = ['1.2']
        result = bot.is_valid_time(time_splits)
        self.assertFalse(result)

    def test_is_valid_time__letters(self):
        time_splits = ['asdf', 'fds']
        result = bot.is_valid_time(time_splits)
        self.assertFalse(result)

class TestParseTime(unittest.TestCase):
    def test_parse_time__all_three(self):
        times = ['4', '10', '54']
        result = bot.parse_time(':'.join(times))

        self.assertEqual(result, int(times[-1]) + 60 * int(times[-2]) + 60*60 * int(times[-3]))

    def test_parse_time__only_two(self):
        times = ['1230', '54']
        result = bot.parse_time(':'.join(times))

        self.assertEqual(result, int(times[-1]) + 60 * int(times[-2]))

    def test_parse_time__only_seconds(self):
        times = ['88']
        result = bot.parse_time(times[0])

        self.assertEqual(result, int(times[-1]))

        result = bot.parse_time(times[0])
        self.assertEqual(result, int(times[-1]))

    def test_parse_time__too_many(self):
        times = ['4', '10', '5', '3']
        result = bot.parse_time(':'.join(times))

        self.assertEqual(result, -1)

    def test_parse_time__wrong_separator(self):
        times = ['4', '10', '5']
        result = bot.parse_time('!'.join(times))

        self.assertEqual(result, -1)

    def test_parse_time__bad_number(self):
        times = ['4', '10as', '5']
        result = bot.parse_time(':'.join(times))

        self.assertEqual(result, -1)

class TestFormatSeconds(unittest.TestCase):
    def test_format_seconds__more_than_one_of_each(self):
        seconds = 7
        seconds += 45*60
        seconds += 3*60*60
        seconds += 6*60*60*24

        time = bot.format_seconds(seconds)
        self.assertEqual(time, "6 days, 3 hours, 45 minutes, and 7 seconds")

    @patch('bot.format_time')
    def test_format_seconds__calls_underlying_function(self, mockClass):
        time = bot.format_seconds(12356)
        self.assertTrue(mockClass.called)

class TestFormatTime(unittest.TestCase):
    def test_format_time__one_of_each_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 22, 7, 3)
        last_infraction_time = infraction_time - datetime.timedelta(days=1, hours=1, minutes=1, seconds=1)

        time = bot.format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "1 day, 1 hour, 1 minute, and 1 second")

    def test_format_time__more_than_a_day_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 22, 7, 3)
        last_infraction_time = infraction_time - datetime.timedelta(days=1, minutes=42)

        time = bot.format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "1 day, 42 minutes, and 0 seconds")

    def test_format_time__less_than_a_day_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 22, 7, 3)
        last_infraction_time = infraction_time - datetime.timedelta(hours=14, minutes=34, seconds=42)

        time = bot.format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "14 hours, 34 minutes, and 42 seconds")

    def test_format_time__less_than_an_hour_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 6, 7, 3)
        last_infraction_time = infraction_time - datetime.timedelta(minutes=34, seconds=42)

        time = bot.format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "34 minutes and 42 seconds")

    def test_format_time__less_than_a_minute_elapsed(self):
        infraction_time = datetime.datetime(2019, 2, 11, 7, 31, 3)
        last_infraction_time = infraction_time - datetime.timedelta(seconds=42)

        time = bot.format_time(infraction_time, last_infraction_time)
        self.assertEqual(time, "42 seconds")

class testCommandParsingAdmin(unittest.TestCase):
    def setUp(self):
        self.author = Mock(**{
                'id': 2,
                'mention': "@test",
                'permissions_in.return_value': Mock(**{
                    'administrator': True
                    }),
                'bot': False
            })

    def test_parse_for_command__VT(self):
        msg = "!vt"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VT)

    def test_parse_for_command__VTSilence_only(self):
        msg = "!vtsilence"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTSILENCE)

    def test_parse_for_command__VTSilence_typo(self):
        msg = "!vtsience"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertNotEqual(cmd, bot.Commands.VTSILENCE)

    def test_parse_for_command__VTSilence_after(self):
        msg = "!vtsilence test"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTSILENCE)

    def test_parse_for_command__VTAlert_only(self):
        msg = "!vtalert"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTALERT)

    def test_parse_for_command__VTSilence_typo(self):
        msg = "!vtaert"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertNotEqual(cmd, bot.Commands.VTALERT)

    def test_parse_for_command__VTSilence_after(self):
        msg = "!vtalert test"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTALERT)

    def test_parse_for_command__VTHelp_only(self):
        msg = "!vthelp"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTHELP)

    def test_parse_for_command__VTLast_only(self):
        msg = "!vtlast"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTLAST)

    def test_parse_for_command__VTCT_only(self):
        msg = "!vtct"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTCT)

    def test_parse_for_command__VTBan_only(self):
        msg = "!vtban"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTBAN)


class testCommandParsingNoAdmin(unittest.TestCase):
    def setUp(self):
        self.author = Mock(**{
                'id': 2,
                'mention': "@test",
                'permissions_in.return_value': Mock(**{
                    'administrator': False
                    }),
                'bot': False
            })

    def test_parse_for_command__VT_only(self):
        msg = "!vt"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VT)

    def test_parse_for_command__VT_after(self):
        msg = "test !vt"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.NOCOMMAND)

    def test_parse_for_command__VT_before(self):
        msg = "!vt testing"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VT)

    def test_parse_for_command__VTAlert_only(self):
        msg = "!vtalert"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.NEEDADMIN)

    def test_parse_for_command__VTSilence_only(self):
        msg = "!vtsilence"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.NEEDADMIN)

    def test_parse_for_command__VTBan_only(self):
        msg = "!vtban"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.NEEDADMIN)

    def test_parse_for_command__VTHelp_only(self):
        msg = "!vthelp"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTHELP)

    def test_parse_for_command__VTLast_only(self):
        msg = "!vtlast"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTLAST)

    def test_parse_for_command__VTCT_only(self):
        msg = "!vtct"
        cmd = bot.parse_for_command(msg, self.author, 1)
        self.assertEqual(cmd, bot.Commands.VTCT)