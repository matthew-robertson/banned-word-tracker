from commands.command import Command

class RemoveBanCommand(Command):
	def __init__(self):
		self.detect_bans_in_message = False

	def is_command_authorized(self, permissions=None):
		return permissions and permissions.administrator

	def execute(self, current_server, current_time, message, author):
		words = message.lstrip().split(' ')[1:]
		if len(words) < 1 or len(words[0]) < 1:
			return "Sorry, I couldn't understand the provided index."
		return self.remove_ban(current_server, words[0], author)

	def remove_ban(self, current_server, ind_str, author):
		try:
			requested_index = int(ind_str) - 1
			if requested_index < 0 or requested_index >= len(current_server.banned_words): raise

			unbanned_word = current_server.unban_word(requested_index)
			if unbanned_word:
				return "Ok {}, '{}' is no longer considered a forbidden word.".format(author.mention, unbanned_word)
			return "Sorry, I couldn't unban that word. You may have tried to unban your only banned word."
		except:
			return "Sorry, I couldn't understand the provided index."