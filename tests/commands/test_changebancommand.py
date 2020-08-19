import unittest
from unittest.mock import patch, Mock
import discord
import datetime

from commands import ChangeBanCommand
from serverobjects.server import DiscordServer

class TestChangeBanCommand(unittest.TestCase):
	def setUp(self):
		self.command = ChangeBanCommand()

	def test_is_command_authorized__no_permissions_disallowed(self):
		result = self.command.is_command_authorized()
		self.assertFalse(result)

	def test_is_command_authorized__non_admin_disallowed(self):
		permissions = discord.Permissions()
		result = self.command.is_command_authorized(permissions)
		self.assertFalse(result)

	def test_is_command_authorized__admin_allowed(self):
		permissions = discord.Permissions.all()
		result = self.command.is_command_authorized(permissions)
		self.assertTrue(result)

	@patch('serverobjects.ban.BanInstance.set_word')
	def test_execute__change_ban_valid(self, word_patch):
		time = datetime.datetime.now()
		server_json = {
			'server_id' : 1,
			'awake' : True,
			'timeout_duration_seconds': 1800,
			'prefix': '!vt',
			'banned_words': [{
				'rowid': 1,
				'server_id': 1,
				'banned_word': 'vore',
				'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
        'record': {
            'record_seconds': 2400,
            'infraction_count': 0
        }
			}]
		}
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtban 1 test",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(server_json, time, None)
		self.command.execute(server, time, message.content, message.author)
		word_patch.assert_called_with('test')
		self.assertTrue(word_patch.called)

	@patch('serverobjects.ban.BanInstance.set_word', side_effect=lambda x: False)
	def test_execute__change_ban_failed(self, word_patch):
		time = datetime.datetime.now()
		server_json = {
			'server_id' : 1,
			'awake' : True,
			'timeout_duration_seconds': 1800,
			'prefix': '!vt',
			'banned_words': [{
				'rowid': 1,
				'server_id': 1,
				'banned_word': 'vore',
				'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
        'record': {
            'record_seconds': 2400,
            'infraction_count': 0
        }
			}]
		}
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtban 1 Vore",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(server_json, time, None)
		result = self.command.execute(server, time, message.content, message.author)
		word_patch.assert_called_with('Vore')
		self.assertEqual(result, "Sorry, I couldn't swap out for this word. It might be confusable for an existing ban?")

	@patch('serverobjects.ban.BanInstance.set_word')
	def test_execute__change_ban_invalid(self, word_patch):
		time = datetime.datetime.now()
		server_json = {
			'server_id' : 1,
			'awake' : True,
			'timeout_duration_seconds': 1800,
			'prefix': '!vt',
			'banned_words': [{
				'rowid': 1,
				'server_id': 1,
				'banned_word': 'vore',
				'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
        'record': {
            'record_seconds': 2400,
            'infraction_count': 0
        }
			}]
		}
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtban 1",
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
      'content': "!vtban asdf asdf",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })

		server = DiscordServer(server_json, time, None)
		self.command.execute(server, time, message.content, message.author)
		self.command.execute(server, time, message2.content, message.author)
		self.assertFalse(word_patch.called)