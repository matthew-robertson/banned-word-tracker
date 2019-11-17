import unittest
from unittest.mock import patch, Mock
import discord
import datetime

from commands import SilenceCommand
from serverobjects.server import DiscordServer

class TestSilenceCommand(unittest.TestCase):
	def setUp(self):
		self.command = SilenceCommand()
		self.author = Mock(**{
			'id': 2,
			'mention': "@test",
			'bot': False
		})

	def test_is_command_authorized__no_permissions_allowed(self):
		result = self.command.is_command_authorized()
		self.assertFalse(result)

	def test_is_command_authorized__non_admin_allowed(self):
		permissions = discord.Permissions()
		result = self.command.is_command_authorized(permissions)
		self.assertFalse(result)

	def test_is_command_authorized__admin_allowed(self):
		permissions = discord.Permissions.all()
		result = self.command.is_command_authorized(permissions)
		self.assertTrue(result)

	@patch('serverobjects.server.DiscordServer.set_awake')
	def test_execute__silence_awake_server(self, awake_patch):
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
		server = DiscordServer(server_json, time, None)
		self.command.execute(server, None, None, self.author)
		awake_patch.assert_called_with(False)
		self.assertTrue(awake_patch.called)