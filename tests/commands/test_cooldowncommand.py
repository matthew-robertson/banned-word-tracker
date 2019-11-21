import unittest
from unittest.mock import patch 
import discord
import datetime

from commands import CooldownCommand
from serverobjects.server import DiscordServer

class TestCooldownCommand(unittest.TestCase):
    def setUp(self):
        self.command = CooldownCommand()

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

    def test_execute__one_word_cooldown(self):
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
            self.command.execute(server, time, "!vtct", None),
            "The cooldown period is 30 minutes and 0 seconds.\n" +
            "I'll be able to issue another alert for 'vore' in 9 minutes and 59 seconds.")

    def test_execute__one_word_available(self):
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
                'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtct", None),
            "The cooldown period is 30 minutes and 0 seconds.\nI'm ready to issue another warning for 'vore' now.")

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
                'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'rowid': 2,
                'server_id': 1,
                'banned_word': 'test',
                'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtct", None),
            "The cooldown period is 30 minutes and 0 seconds.\n" +
            "I'm ready to issue another warning for 'vore' now.\n" +
            "I'll be able to issue another alert for 'test' in 9 minutes and 59 seconds.")

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
                'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'rowid': 2,
                'server_id': 1,
                'banned_word': 'test',
                'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtct 1", None),
            "The cooldown period is 30 minutes and 0 seconds.\n" +
            "I'm ready to issue another warning for 'vore' now.")
        self.assertEqual(
            self.command.execute(server, time, "!vtct 2", None),
            "The cooldown period is 30 minutes and 0 seconds.\n" +
            "I'll be able to issue another alert for 'test' in 9 minutes and 59 seconds.")

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
                'calledout_at': (time - datetime.timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'rowid': 2,
                'server_id': 1,
                'banned_word': 'test',
                'infracted_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                'calledout_at': (time - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        server = DiscordServer(server_json, time, None)
        self.assertEqual(
            self.command.execute(server, time, "!vtct -1", None),
            "The cooldown period is 30 minutes and 0 seconds.\n" +
            "I'm ready to issue another warning for 'vore' now.\n" +
            "I'll be able to issue another alert for 'test' in 9 minutes and 59 seconds.")
        self.assertEqual(
            self.command.execute(server, time, "!vtct 5", None),
            "The cooldown period is 30 minutes and 0 seconds.\n" +
            "I'm ready to issue another warning for 'vore' now.\n" +
            "I'll be able to issue another alert for 'test' in 9 minutes and 59 seconds.")