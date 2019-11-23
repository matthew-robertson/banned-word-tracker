from commands.command import Command

class ChangeBanCommand(Command):
	def __init__(self):
		self.detect_bans_in_message = False

	def is_command_authorized(self, permissions=None):
		return permissions and permissions.administrator

	def execute(self, current_server, current_time, message, author):
		words = message.lstrip().split(' ')[1:]
		new_word = words[0]
		if len(new_word) < 1:
			return "Sorry, I can't ban the empty string. Please try a message of the form '!vtban [wordToBan]'"

		current_server.banned_words[0].set_word(new_word)
		return "Ok {}, '{}' is now considered a forbidden word.".format(author.mention, new_word)