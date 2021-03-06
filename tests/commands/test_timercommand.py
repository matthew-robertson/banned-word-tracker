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
		server = DiscordServer(server_json, time, None)
		self.assertEqual(
			self.command.execute(server, time, "!vt", None),
			"1, 'vore': 20 minutes and 0 seconds.")

	def test_execute__multiple_words(self):
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
			},
			{
				'rowid': 2,
				'server_id': 1,
				'banned_word': 'test',
				'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
        'record': {
            'record_seconds': 2400,
            'infraction_count': 0
        }
			}]
		}
		server = DiscordServer(server_json, time, None)
		self.assertEqual(
			self.command.execute(server, time, "!vt", None),
			"1, 'vore': 20 minutes and 0 seconds.\n" +
			"2, 'test': 40 minutes and 0 seconds.")

	def test_execute__one_of_multiple(self):
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
			},
			{
				'rowid': 2,
				'server_id': 1,
				'banned_word': 'test',
				'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
        'record': {
            'record_seconds': 2400,
            'infraction_count': 0
        }
			}]
		}
		server = DiscordServer(server_json, time, None)
		self.assertEqual(
			self.command.execute(server, time, "!vt 1", None),
			"'vore': 20 minutes and 0 seconds.")
		self.assertEqual(
			self.command.execute(server, time, "!vt 2", None),
			"'test': 40 minutes and 0 seconds.")

	def test_execute__out_of_range(self):
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
			},
			{
				'rowid': 2,
				'server_id': 1,
				'banned_word': 'test',
				'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
				'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
        'record': {
            'record_seconds': 2400,
            'infraction_count': 0
        }
			}]
		}
		server = DiscordServer(server_json, time, None)
		self.assertEqual(
			self.command.execute(server, time, "!vt 3", None),
			"1, 'vore': 20 minutes and 0 seconds.\n" +
			"2, 'test': 40 minutes and 0 seconds.")
		self.assertEqual(
			self.command.execute(server, time, "!vt -1", None),
			"1, 'vore': 20 minutes and 0 seconds.\n" +
			"2, 'test': 40 minutes and 0 seconds.")