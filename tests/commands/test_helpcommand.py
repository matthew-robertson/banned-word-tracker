import unittest
import discord

from commands import HelpCommand

class TestHelpCommand(unittest.TestCase):
	def setUp(self):
		self.command = HelpCommand()

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