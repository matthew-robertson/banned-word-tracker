from confusables import is_confusable
from commands.command import Command

class RemoveBanWordCommand(Command):
	def __init__(self):
		self.detect_bans_in_message = False

	def is_command_authorized(self, permissions=None):
		return permissions and permissions.administrator

	def execute(self, current_server, current_time, message, author):
		words = message.lstrip().split(' ')[1:]
		if len(words) < 1 or len(words[0]) < 1:
			return "Sorry, I couldn't understand your command. Make sure to include a word to unban."
		return self.remove_ban(current_server, words[0], author)

	def remove_ban(self, current_server, unban_str, author):
		requested_index = [ind for ind, ban in enumerate(current_server.banned_words) if is_confusable(unban_str, ban.banned_word)]
		if not len(requested_index):
			return "Sorry, I couldn't find a matching word to unban."
		unbanned_word = current_server.unban_word(requested_index[0])
		if unbanned_word:
			return "Ok {}, '{}' is no longer considered a forbidden word.".format(author.mention, unbanned_word)
		return "Sorry, I couldn't unban that word. You may have tried to unban your only banned word."