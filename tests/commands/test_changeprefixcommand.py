import unittest
from unittest.mock import patch, Mock
import discord
import datetime

from commands import ChangePrefixCommand
from serverobjects.server import DiscordServer

class TestChangePrefixCommand(unittest.TestCase):
	def setUp(self):
		self.command = ChangePrefixCommand()
		self.time = datetime.datetime.now()
		self.server_json = {
			'server_id' : 1,
			'awake' : True,
			'timeout_duration_seconds': 1800,
			'prefix': '!vt',
			'banned_words': [{
				'rowid': 1,
				'server_id': 1,
				'banned_word': 'vore',
				'infracted_at': (self.time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (self.time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
        'record': {
            'record_seconds': 2400,
            'infraction_count': 0
        }
			}]
		}

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

	@patch('serverobjects.server.DiscordServer.update_server_settings')
	def test_execute__change_full_time_valid(self, prefix_patch):
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtprefix !testin",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(self.server_json, self.time, None)
		retval = self.command.execute(server, self.time, message.content, message.author)
		prefix_patch.assert_called_with({ 'prefix': '!testin' })
		self.assertEqual(
			retval,
			"Cool, from now on you'll need to start a message with '!testin' for me to treat it as a command."
		)
		self.assertTrue(prefix_patch.called)

	@patch('serverobjects.server.DiscordServer.update_server_settings')
	def test_execute__change_prefix_too_long(self, prefix_patch):
		prefix_patch.return_value = False

		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtprefix asdfasdfasdf",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(self.server_json, self.time, None)
		retval = self.command.execute(server, self.time, message.content, message.author)
		self.assertEqual(
			retval,
			"Sorry, I don't understand that formatting. I was expecting a new prefix between 1 and 10 characters long."
		)

	@patch('serverobjects.server.DiscordServer.update_server_settings')
	def test_execute__change_no_time_invalid(self, prefix_patch):
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtprefix",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(self.server_json, self.time, None)
		self.command.execute(server, self.time, message.content, message.author)
		self.assertFalse(prefix_patch.called)