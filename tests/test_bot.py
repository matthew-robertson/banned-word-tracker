import unittest
import datetime
from unittest.mock import Mock

import bot

class TestAwakeNoCooldownBot(unittest.TestCase):
    def setUp(self):
        self.current_time = datetime.datetime.now()
        self.current_server = {
            'server_id' : 1,
            'infracted_at': self.current_time - datetime.timedelta(minutes=30),
            'calledout_at': self.current_time - datetime.timedelta(minutes=30),
            'awake' : True
        }
        self.server_dao = Mock(**{
            'get_server.return_value': self.current_server,
            'insert_server.return_value': None
        })
        self.infringedString = "@test referenced the forbidden word, setting the counter back to 0. I'll wait a half hour before warning you again.\n The server went 30 minutes and 0 seconds without mentioning it."

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

        message_to_send = bot.handle_message(self.server_dao, message, 1)
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

        message_to_send = bot.handle_message(self.server_dao, message, 1)
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

        message_to_send = bot.handle_message(self.server_dao, message, 1)
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

        message_to_send = bot.handle_message(self.server_dao, message, 1)
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

        message_to_send = bot.handle_message(self.server_dao, message, 1)
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
            'content': "**v**o**r**e**D",
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
            'content': "|||v||||o||||r||e||s",
            'author': Mock(**{
                'id': 2,
                'mention': "@test",
                'bot': False
            }),
        })

        message_to_send1 = bot.handle_message(self.server_dao, message1, 1)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send2 = bot.handle_message(self.server_dao, message2, 1)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send3 = bot.handle_message(self.server_dao, message3, 1)
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

        message_to_send1 = bot.handle_message(self.server_dao, message1, 1)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send2 = bot.handle_message(self.server_dao, message2, 1)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send3 = bot.handle_message(self.server_dao, message3, 1)
        self.assertEqual(message_to_send1, self.infringedString)

class TestAwakeCooldownBot(unittest.TestCase):
    def setUp(self):
        self.current_time = datetime.datetime.now()
        self.current_server = {
            'server_id' : 1,
            'infracted_at': self.current_time - datetime.timedelta(minutes=30),
            'calledout_at': self.current_time - datetime.timedelta(minutes=20),
            'awake' : True
        }
        self.server_dao = Mock(**{
            'get_server.return_value': self.current_server,
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
        message_to_send = bot.handle_message(self.server_dao, message, 1)

        self.assertEqual(message_to_send, False)

class TestAsleepBot(unittest.TestCase):
    def setUp(self):
        self.current_time = datetime.datetime.now()
        self.current_server = {
            'server_id' : 1,
            'infracted_at': self.current_time - datetime.timedelta(minutes=30),
            'calledout_at': self.current_time - datetime.timedelta(minutes=40),
            'awake' : False
        }
        self.server_dao = Mock(**{
            'get_server.return_value': self.current_server,
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
        message_to_send = bot.handle_message(self.server_dao, message, 1)

        self.assertEqual(message_to_send, False)

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
                'server_permissions': Mock(**{
                    'administrator': True
                    }),
                'bot': False
            })

    def test_parse_for_command__VT(self):
        msg = "!vt"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VT)

    def test_parse_for_command__VTSilence_only(self):
        msg = "!vtsilence"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VTSILENCE)

    def test_parse_for_command__VTSilence_typo(self):
        msg = "!vtsience"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertNotEqual(cmd, bot.Commands.VTSILENCE)

    def test_parse_for_command__VTSilence_after(self):
        msg = "!vtsilence test"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VTSILENCE)

    def test_parse_for_command__VTAlert_only(self):
        msg = "!vtalert"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VTALERT)

    def test_parse_for_command__VTSilence_typo(self):
        msg = "!vtaert"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertNotEqual(cmd, bot.Commands.VTALERT)

    def test_parse_for_command__VTSilence_after(self):
        msg = "!vtalert test"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VTALERT)

    def test_parse_for_command__VTHelp_only(self):
        msg = "!vthelp"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VTHELP)

    def test_parse_for_command__VTLast_only(self):
        msg = "!vtlast"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VTLAST)


class testCommandParsingNoAdmin(unittest.TestCase):
    def setUp(self):
        self.author = Mock(**{
                'id': 2,
                'mention': "@test",
                'server_permissions': Mock(**{
                    'administrator': False
                    }),
                'bot': False
            })

    def test_parse_for_command__VT_only(self):
        msg = "!vt"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VT)

    def test_parse_for_command__VT_after(self):
        msg = "test !vt"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.NOCOMMAND)

    def test_parse_for_command__VT_before(self):
        msg = "!vt testing"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VT)

    def test_parse_for_command__VTAlert_only(self):
        msg = "!vtalert"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.NEEDADMIN)

    def test_parse_for_command__VTSilence_only(self):
        msg = "!vtsilence"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.NEEDADMIN)

    def test_parse_for_command__VTHelp_only(self):
        msg = "!vthelp"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VTHELP)

    def test_parse_for_command__VTLast_only(self):
        msg = "!vtlast"
        cmd = bot.parse_for_command(msg, self.author)
        self.assertEqual(cmd, bot.Commands.VTLAST)