import unittest
import discord
import datetime

from commands import TimerCommand
from serverobjects.server import DiscordServer

class TestTimerCommand(unittest.TestCase):
	def setUp(self):
		self.command = TimerCommand()

	def test_is_command_authorized__no_permissions_allowed(self):
		result = self.command.is_command_authorized()
		self.assertTrue(result)

	def test_is_command_authorized__non_admin_allowed(self):
		permissions = discord.Permissions()
		result = self.command.is_command_authorized(permissions)
		self.assertTrue(result)

	def test_is_command_authorized__admin_allowed(self):
		permissions = discord.Permissions.all()
		result = self.command.is_command_authorized(permissions)
		self.assertTrue(result)

	def test_execute__one_word(self):
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
		self.assertEqual(
			self.command.execute(server, time, "!vt", None),
			"The server has gone 20 minutes and 0 seconds without mentioning 'vore'.")

	def test_execute__multiple_words(self):
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
				'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
			}]
		}
		server = DiscordServer(server_json, time, None)
		self.assertEqual(
			self.command.execute(server, time, "!vt", None),
			"The server has gone 20 minutes and 0 seconds without mentioning 'vore'.\n" +
			"The server has gone 40 minutes and 0 seconds without mentioning 'test'.")

	def test_execute__one_of_multiple(self):
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
				'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
			}]
		}
		server = DiscordServer(server_json, time, None)
		self.assertEqual(
			self.command.execute(server, time, "!vt 1", None),
			"The server has gone 20 minutes and 0 seconds without mentioning 'vore'.")
		self.assertEqual(
			self.command.execute(server, time, "!vt 2", None),
			"The server has gone 40 minutes and 0 seconds without mentioning 'test'.")

	def test_execute__out_of_range(self):
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
				'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
			}]
		}
		server = DiscordServer(server_json, time, None)
		self.assertEqual(
			self.command.execute(server, time, "!vt 3", None),
			"The server has gone 20 minutes and 0 seconds without mentioning 'vore'.\n" +
			"The server has gone 40 minutes and 0 seconds without mentioning 'test'.")
		self.assertEqual(
			self.command.execute(server, time, "!vt -1", None),
			"The server has gone 20 minutes and 0 seconds without mentioning 'vore'.\n" +
			"The server has gone 40 minutes and 0 seconds without mentioning 'test'.")