import unittest
import datetime
from unittest.mock import Mock, patch
from types import MethodType

import bot
from commands import TimerCommand, CooldownCommand, HelpCommand, SilenceCommand, AlertCommand, ChangeBanCommand, AddBanCommand, RemoveBanCommand, ChangeTimeCommand, NoCommand
from serverobjects import DiscordServer, BanInstance

@patch.object(DiscordServer, 'update_server_settings')
@patch.object(BanInstance, 'send_infringing_message')
class TestAwakeNoCooldownBot(unittest.TestCase):
    def simple_server(server, time, session):
        current_server = {
            'server_id' : 1,
            'awake' : True,
            'timeout_duration_seconds': 1800,
            'banned_words': [{
                'rowid': 1,
                'server_id': 1,
                'banned_word': 'vore',
                'infracted_at': (time - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'rowid': 2,
                'server_id': 2,
                'banned_word': 'bepis',
                'infracted_at': (time - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        return DiscordServer(current_server, time, None)

    def setUp(self):
        self.current_time = datetime.datetime.now()
        self.infringedString = "@test referenced a forbidden word, setting its counter back to 0.\n"
        self.infringedString += "I'll wait 30 minutes and 0 seconds before warning you for this word again.\n"
        self.infringedString += "The server went 30 minutes and 0 seconds without mentioning the forbidden word 'vore'."

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__different_word(self, sPostMock, bPostMock, fetchMock):
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

        message_to_send = bot.handle_message(message, self.current_time, None)

        infringedString = "@test referenced a forbidden word, setting its counter back to 0.\n"
        infringedString += "I'll wait 30 minutes and 0 seconds before warning you for this word again.\n"
        infringedString += "The server went 30 minutes and 0 seconds without mentioning the forbidden word 'bepis'."
        self.assertEqual(message_to_send, infringedString)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__valid_post(self, sPostMock, bPostMock, fetchMock):
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

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertFalse(message_to_send)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__infringing_post_only(self, sPostMock, bPostMock, fetchMock):
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

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertEqual(message_to_send, self.infringedString)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__infringing_post_embedded(self, sPostMock, bPostMock, fetchMock):
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

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertEqual(message_to_send, self.infringedString)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__infringing_post_from_bot(self, sPostMock, bPostMock, fetchMock):
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

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertFalse(message_to_send)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__infringing_post_embedded_hyphen(self, sPostMock, bPostMock, fetchMock):
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

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertEqual(message_to_send, self.infringedString)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__infringing_post_formatting(self, sPostMock, bPostMock, fetchMock):
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

        message_to_send1 = bot.handle_message(message1, self.current_time, None)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send2 = bot.handle_message(message2, self.current_time, None)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send3 = bot.handle_message(message3, self.current_time, None)
        self.assertEqual(message_to_send1, self.infringedString)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__infringing_post_unicode(self, sPostMock, bPostMock, fetchMock):
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

        message_to_send1 = bot.handle_message(message1, self.current_time, None)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send2 = bot.handle_message(message2, self.current_time, None)
        self.assertEqual(message_to_send1, self.infringedString)
        message_to_send3 = bot.handle_message(message3, self.current_time, None)
        self.assertEqual(message_to_send1, self.infringedString)

@patch.object(DiscordServer, 'update_server_settings')
@patch.object(BanInstance, 'send_infringing_message')
class TestAwakeCooldownBot(unittest.TestCase):
    def simple_server(server, time, session):
        current_server = {
            'server_id' : 1,
            'awake' : True,
            'timeout_duration_seconds': 1800,
            'banned_words': [{
                'rowid': 1,
                'server_id': 1,
                'banned_word': 'vore',
                'infracted_at': (time - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        return DiscordServer(current_server, time, None)

    def setUp(self):
        self.current_time = datetime.datetime.now()

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__infringing_post(self, sPostMock, bPostMock, fetchMock):
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
        message_to_send = bot.handle_message(message, self.current_time, None)

        self.assertEqual(message_to_send, '')

@patch.object(DiscordServer, 'update_server_settings')
@patch.object(BanInstance, 'send_infringing_message')
class TestAsleepBot(unittest.TestCase):
    def simple_server(server, time, session):
        current_server = {
            'server_id' : 1,
            'awake' : False,
            'timeout_duration_seconds': 1800,
            'banned_words': [{
                'rowid': 1,
                'server_id': 1,
                'banned_word': 'vore',
                'infracted_at': (time - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        return DiscordServer(current_server, time, None)

    def setUp(self):
        self.current_time = datetime.datetime.now()

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    def test_handle_message__infringing_post(self, sPostMock, bPostMock, fetchMock):
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
        message_to_send = bot.handle_message(message, self.current_time, None)

        self.assertEqual(message_to_send, '')

class TestBotCallsCommands(unittest.TestCase):
    def simple_server(server, time, session):
        current_server = {
            'server_id' : 1,
            'awake' : True,
            'timeout_duration_seconds': 1800,
            'banned_words': [{
                'rowid': 1,
                'server_id': 1,
                'banned_word': 'vore',
                'infracted_at': (time - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        return DiscordServer(current_server, time, None)

    def setUp(self):
        self.current_time = datetime.datetime.now()
        self.nonadmin = Mock(**{
                'id': 2,
                'mention': "@test",
                'permissions_in.return_value': Mock(**{
                    'administrator': False
                    }),
                'bot': False
            })
        self.admin = Mock(**{
                'id': 2,
                'mention': "@test",
                'permissions_in.return_value': Mock(**{
                    'administrator': True
                    }),
                'bot': False
            })

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(NoCommand, 'execute')
    def test_handle_message__no_command(self, noMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vttest",
            'author': self.nonadmin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(noMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(TimerCommand, 'execute')
    def test_handle_message__VT(self, vtMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vt",
            'author': self.nonadmin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(vtMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(TimerCommand, 'execute')
    def test_handle_message__VT_extra(self, vtMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vt test",
            'author': self.nonadmin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(vtMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(ChangeTimeCommand, 'execute')
    def test_handle_message__VT_delay_nonadmin(self, timeMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vtdelay 1",
            'author': self.nonadmin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertFalse(timeMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(ChangeTimeCommand, 'execute')
    def test_handle_message__VT_delay_admin(self, timeMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vtdelay 1",
            'author': self.admin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(timeMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(AddBanCommand, 'execute')
    def test_handle_message__VT_ban_admin(self, banMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vtban 1",
            'author': self.admin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(banMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(RemoveBanCommand, 'execute')
    def test_handle_message__VT_ban_admin(self, banMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vtunban 1",
            'author': self.admin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(banMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(CooldownCommand, 'execute')
    def test_handle_message__VT_ct(self, ctMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vtct",
            'author': self.admin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(ctMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(HelpCommand, 'execute')
    def test_handle_message__VT_help(self, helpMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vthelp",
            'author': self.admin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(helpMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(AlertCommand, 'execute')
    def test_handle_message__VT_alert(self, alertMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vtalert",
            'author': self.admin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(alertMock.called)

    @patch('bot.fetch_server_from_api', side_effect=simple_server)
    @patch.object(SilenceCommand, 'execute')
    def test_handle_message__VT_silence(self, silenceMock, sMock):
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "!vtsilence",
            'author': self.admin,
        })

        message_to_send = bot.handle_message(message, self.current_time, None)
        self.assertTrue(silenceMock.called)