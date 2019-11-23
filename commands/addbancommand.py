from commands.command import Command

class AddBanCommand(Command):
	def __init__(self):
		self.detect_bans_in_message = False

	def is_command_authorized(self, permissions=None):
		return permissions and permissions.administrator

	def execute(self, current_server, current_time, message, author):
		words = message.lstrip().split(' ')[1:]
		if len(words) < 1 or len(words[0]) < 1: return "Sorry, I can't ban nothing. Please specify a word to ban."

		ban_succeeded = current_server.ban_new_word(words[0])
		if ban_succeeded:
			return "Ok {}, '{}' is now considered a forbidden word.".format(author.mention, words[0])
		return "Sorry, I couldn't ban that word. You might have too many words banned, or you may have already banned this word."