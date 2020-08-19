import unittest
from unittest.mock import patch, Mock
import discord
import datetime

from commands import ChangeTimeCommand
from serverobjects.server import DiscordServer

class TestChangeTimeCommand(unittest.TestCase):
	def setUp(self):
		self.command = ChangeTimeCommand()
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
	def test_execute__change_full_time_valid(self, time_patch):
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtdelay 1:1:1",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(self.server_json, self.time, None)
		retval = self.command.execute(server, self.time, message.content, message.author)
		time_patch.assert_called_with({ 'timeout_duration_seconds': 1+1*60+1*60*60 })
		self.assertEqual(
			retval,
			"Cool, from now on I'll wait at least 1 hour, 1 minute, and 1 second between alerts."
		)
		self.assertTrue(time_patch.called)

	@patch('serverobjects.server.DiscordServer.update_server_settings')
	def test_execute__change_second_time_valid(self, time_patch):
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtdelay 45",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(self.server_json, self.time, None)
		retval = self.command.execute(server, self.time, message.content, message.author)
		time_patch.assert_called_with({ 'timeout_duration_seconds': 45 })
		self.assertEqual(
			retval,
			"Cool, from now on I'll wait at least 45 seconds between alerts."
		)
		self.assertTrue(time_patch.called)

	@patch('serverobjects.server.DiscordServer.update_server_settings')
	def test_execute__change_second_too_long(self, time_patch):
		time_patch.return_value = False

		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtdelay 777777777777",
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
			"Sorry, something went wrong and I couldn't update the delay. Make sure the delay is under 100 million seconds (~3 years)"
		)

	@patch('serverobjects.server.DiscordServer.set_timeout')
	def test_execute__change_extra_invalid(self, time_patch):
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtdelay 1:1:1:1",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(self.server_json, self.time, None)
		self.command.execute(server, self.time, message.content, message.author)
		self.assertFalse(time_patch.called)

	@patch('serverobjects.server.DiscordServer.set_timeout')
	def test_execute__change_no_time_invalid(self, time_patch):
		message = Mock(**{
      'server': Mock(**{
        'id': 1
      }),
      'content': "!vtdelay",
      'author': Mock(**{
        'id': 2,
        'mention': "@test",
        'bot': False
      }),
    })
		server = DiscordServer(self.server_json, self.time, None)
		self.command.execute(server, self.time, message.content, message.author)
		self.assertFalse(time_patch.called)