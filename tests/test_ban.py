import unittest
import datetime
from unittest.mock import Mock, patch
from types import MethodType

from serverobjects.ban import BanInstance

class TestCheckIfMessageInfringes(unittest.TestCase):
	def test_check_if_message_infringes__exact_match(self):
		test_ban = BanInstance(
			{	'rowid': 1, 'banned_word': 'test', 'calledout_at': '2019-11-11 11:11:11',	'infracted_at': '2019-11-11 11:11:11','server_id': 1234 },
			datetime.datetime.now(),
			0)
		self.assertTrue(test_ban.check_if_message_infringes('test'))

	def test_check_if_message_infringes__embedded_match(self):
		test_ban = BanInstance(
			{	'rowid': 1, 'banned_word': 'test', 'calledout_at': '2019-11-11 11:11:11',	'infracted_at': '2019-11-11 11:11:11','server_id': 1234 },
			datetime.datetime.now(),
			0)
		self.assertTrue(test_ban.check_if_message_infringes('this is a test message.'))

	def test_check_if_message_infringes__no_match(self):
		test_ban = BanInstance(
			{	'rowid': 1, 'banned_word': 'test', 'calledout_at': '2019-11-11 11:11:11',	'infracted_at': '2019-11-11 11:11:11','server_id': 1234 },
			datetime.datetime.now(),
			0)
		self.assertFalse(test_ban.check_if_message_infringes('this message does not infringe.'))

	def test_check_if_message_infringes__word_embedded_in_other(self):
		test_ban = BanInstance(
			{	'rowid': 1, 'banned_word': 'vore', 'calledout_at': '2019-11-11 11:11:11',	'infracted_at': '2019-11-11 11:11:11','server_id': 1234 },
			datetime.datetime.now(),
			0)
		self.assertFalse(test_ban.check_if_message_infringes('omnivore'))

	def test_check_if_message_infringes__at_mention_test(self):
		test_ban = BanInstance(
			{	'rowid': 1, 'banned_word': '<@12345>', 'calledout_at': '2019-11-11 11:11:11',	'infracted_at': '2019-11-11 11:11:11','server_id': 1234 },
			datetime.datetime.now(),
			0)
		self.assertTrue(test_ban.check_if_message_infringes(' <@12345> '))
		self.assertTrue(test_ban.check_if_message_infringes('<@12345>'))

	def test_check_if_message_infringes__similar_word_unicode(self):
		test_ban = BanInstance(
			{	'rowid': 1, 'banned_word': 'vore', 'calledout_at': '2019-11-11 11:11:11',	'infracted_at': '2019-11-11 11:11:11','server_id': 1234 },
			datetime.datetime.now(),
			0)
		self.assertTrue(test_ban.check_if_message_infringes('vÒrË'))
		self.assertTrue(test_ban.check_if_message_infringes('vᴑRè'))

	def test_check_if_message_infringes__similar_word_formatting(self):
		test_ban = BanInstance(
			{	'rowid': 1, 'banned_word': 'vore', 'calledout_at': '2019-11-11 11:11:11',	'infracted_at': '2019-11-11 11:11:11','server_id': 1234 },
			datetime.datetime.now(),
			0)
		self.assertTrue(test_ban.check_if_message_infringes('-v-o-r-e-'))
		self.assertTrue(test_ban.check_if_message_infringes('**v**o**r**e**'))
		self.assertTrue(test_ban.check_if_message_infringes('|||v||||o||||r||e|||'))
