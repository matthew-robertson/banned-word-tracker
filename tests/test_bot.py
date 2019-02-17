import unittest
import datetime
from unittest.mock import Mock

import bot

class TestBot(unittest.TestCase):

    def test_handle_message__valid_post(self):
        current_server = {
            'server_id' : 1,
            'infracted_at': datetime.datetime.now() - datetime.timedelta(minutes=30),
            'calledout_at': datetime.datetime.now() - datetime.timedelta(minutes=30),
            'awake' : True
        }
        server_dao = Mock(**{
            'get_server.return_value': current_server,
            'insert_server.return_value': None
        })
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "I am a good boy",
            'author': Mock(**{
                'id': 2,
                'mention': "@test"
            }),
        })
        message_to_send = bot.handle_message(server_dao, message, 1)

        self.assertFalse(message_to_send)

    def test_handle_message__infringing_post(self):
        current_server = {
            'server_id' : 1,
            'infracted_at': datetime.datetime.now() - datetime.timedelta(minutes=30),
            'calledout_at': datetime.datetime.now() - datetime.timedelta(minutes=30),
            'awake' : True
        }
        server_dao = Mock(**{
            'get_server.return_value': current_server,
            'insert_server.return_value': None
        })
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "vore",
            'author': Mock(**{
                'id': 2,
                'mention': "@test"
            }),
        })
        message_to_send = bot.handle_message(server_dao, message, 1)

        self.assertEqual(message_to_send, "@test referenced the forbidden word, setting the counter back to 0. I'll wait a half hour before warning you again.\n The server went 30 minutes and 0 seconds without mentioning it.")

    def test_handle_message__infringing_post_on_cooldown(self):
        current_server = {
            'server_id' : 1,
            'infracted_at': datetime.datetime.now() - datetime.timedelta(minutes=30),
            'calledout_at': datetime.datetime.now() - datetime.timedelta(minutes=20),
            'awake' : True
        }
        server_dao = Mock(**{
            'get_server.return_value': current_server,
            'insert_server.return_value': None
        })
        message = Mock(**{
            'server': Mock(**{
                'id': 1
            }),
            'content': "vore",
            'author': Mock(**{
                'id': 2,
                'mention': "@test"
            }),
        })
        message_to_send = bot.handle_message(server_dao, message, 1)

        self.assertEqual(message_to_send, False)
