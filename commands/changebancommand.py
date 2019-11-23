from commands.command import Command

class ChangeBanCommand(Command):
	def __init__(self):
		self.detect_bans_in_message = False

	def is_command_authorized(self, permissions=None):
		return permissions and permissions.administrator

	def execute(self, current_server, current_time, message, author):
		words = message.lstrip().split(' ')[1:]
		banned_words = current_server.banned_words
		try:
			requested_index = int(words[0]) - 1
			new_word = words[1]
			if requested_index < 0 or requested_index >= len(banned_words): raise
			if len(new_word) < 1: raise
			
			old_word = banned_words[requested_index].banned_word
			did_swap = banned_words[requested_index].set_word(new_word)
			if did_swap:
				return "Ok {}, '{}' has replaced '{}' as a forbidden word.".format(author.mention, new_word, old_word)
			return "Sorry, I couldn't swap out for this word. It might be confusable for an existing ban?"
		except:
			return "Sorry, I couldn't understand that command. Make sure you're using a valid index and a non-empty word."

		