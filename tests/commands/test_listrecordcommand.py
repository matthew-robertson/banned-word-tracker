import unittest
from unittest.mock import patch 
import discord
import datetime

from commands import ListRecordCommand
from serverobjects.server import DiscordServer

class TestCooldownCommand(unittest.TestCase):
    def setUp(self):
        self.command = ListRecordCommand()

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

    def test_execute__one_word_record_is_longest(self):
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
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'record': {
                    'record_seconds': 2400,
                    'infraction_count': 1
                }
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtr", None),
           "The server has said 'vore' 1 time.\nThe server's longest streak without saying 'vore' is 40 minutes and 0 seconds.")

    def test_execute__one_word_record_is_current(self):
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
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'record': {
                    'record_seconds': 600,
                    'infraction_count': 20
                }
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtr", None),
            "The server has said 'vore' 20 times.\nThe server's currently on its longest streak without saying 'vore': 20 minutes and 0 seconds.")

    def test_execute__multiple_words_mixed(self):
        time = datetime.datetime.now()
        server_json = {
            'server_id' : 1,
            'awake' : True,
            'timeout_duration_seconds': 1800,
            'banned_words': [{
                'rowid': 1,
                'server_id': 1,
                'banned_word': 'vore',
                'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
                'record': {
                    'record_seconds': 1200,
                    'infraction_count': 0
                }
            },
            {
                'rowid': 2,
                'server_id': 1,
                'banned_word': 'test',
                'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'record': {
                    'record_seconds': 2400,
                    'infraction_count': 20
                }
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtct", None),
            "The server has said 'vore' 0 times.\nThe server's currently on its longest streak without saying 'vore': 40 minutes and 0 seconds.\n\n" +
            "The server has said 'test' 20 times.\nThe server's longest streak without saying 'test' is 40 minutes and 0 seconds.")

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
                'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
                'record': {
                    'record_seconds': 1200,
                    'infraction_count': 1
                }
            },
            {
                'rowid': 2,
                'server_id': 1,
                'banned_word': 'test',
                'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'record': {
                    'record_seconds': 2400,
                    'infraction_count': 20
                }
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtr 1", None),
            "The server has said 'vore' 1 time.\nThe server's currently on its longest streak without saying 'vore': 40 minutes and 0 seconds.")
        self.assertEqual(
            self.command.execute(server, time, "!vtr 2", None),
            "The server has said 'test' 20 times.\nThe server's longest streak without saying 'test' is 40 minutes and 0 seconds.")

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
                'infracted_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
                'record': {
                    'record_seconds': 1200,
                    'infraction_count': 0
                }
            },
            {
                'rowid': 2,
                'server_id': 1,
                'banned_word': 'test',
                'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'record': {
                    'record_seconds': 2400,
                    'infraction_count': 69
                }
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtr -1", None),
            "The server has said 'vore' 0 times.\nThe server's currently on its longest streak without saying 'vore': 40 minutes and 0 seconds.\n\n" +
            "The server has said 'test' 69 times.\nThe server's longest streak without saying 'test' is 40 minutes and 0 seconds.")
        self.assertEqual(
            self.command.execute(server, time, "!vtr 5", None),
            "The server has said 'vore' 0 times.\nThe server's currently on its longest streak without saying 'vore': 40 minutes and 0 seconds.\n\n" +
            "The server has said 'test' 69 times.\nThe server's longest streak without saying 'test' is 40 minutes and 0 seconds.")