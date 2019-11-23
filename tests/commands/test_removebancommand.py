import unittest
from unittest.mock import patch, Mock
import discord
import datetime

from commands import RemoveBanCommand
from serverobjects.server import DiscordServer

class TestRemoveBanCommand(unittest.TestCase):
	def setUp(self):
		self.command = RemoveBanCommand()

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

	@patch('serverobjects.server.DiscordServer.unban_word')
	def test_execute__remove_ban_valid(self, word_patch):
		time = datetime.datetime.now()
		server_json = {
			'server_id' : 1,
			'awake' : True,
			'timeout_duration_seconds': 1800,
			'banned_words': [{
				'rowid': 1,
				'server_id': 1,
				'banned_word': 'vore',
				'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
			},
			{
				'rowid': 2,
				'server_id': 1,
				'banned_word': 'test',
				'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
			}]
		}
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtunban 1",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(server_json, time, None)
		self.command.execute(server, time, message.content, message.author)
		word_patch.assert_called_with(0)
		self.assertTrue(word_patch.called)

	@patch('serverobjects.server.DiscordServer.unban_word', side_effect=lambda x: False)
	def test_execute__remove_ban_bad_index(self, word_patch):
		time = datetime.datetime.now()
		server_json = {
			'server_id' : 1,
			'awake' : True,
			'timeout_duration_seconds': 1800,
			'banned_words': [{
				'rowid': 1,
				'server_id': 1,
				'banned_word': 'vore',
				'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
			}]
		}
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtban test",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(server_json, time, None)
		result = self.command.execute(server, time, message.content, message.author)
		self.assertEqual(result, "Sorry, I couldn't understand the provided index.")

	@patch('serverobjects.server.DiscordServer.unban_word', side_effect=lambda x: False)
	def test_execute__remove_ban_failed(self, word_patch):
		time = datetime.datetime.now()
		server_json = {
			'server_id' : 1,
			'awake' : True,
			'timeout_duration_seconds': 1800,
			'banned_words': [{
				'rowid': 1,
				'server_id': 1,
				'banned_word': 'vore',
				'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
			}]
		}
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtunban 1",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(server_json, time, None)
		result = self.command.execute(server, time, message.content, message.author)
		self.assertEqual(result, "Sorry, I couldn't unban that word. You may have tried to unban your only banned word.")