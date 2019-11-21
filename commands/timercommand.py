from commands.command import Command
from utils.time import format_time

class TimerCommand(Command):
	def get_banned_word_text(self, ban, current_time):
		time_lasted = format_time(current_time, ban.infracted_at)
		return "The server has gone {} without mentioning '{}'.".format(time_lasted, ban.banned_word)

	def execute(self, current_server, current_time, message, author):
		banned_words = current_server.banned_words
		try:
			requested_index = int(message.split(" ")[1]) - 1
			if requested_index < 0 or requested_index >= len(banned_words): raise
			return self.get_banned_word_text(banned_words[requested_index], current_time)
		except:
			return "\n".join(map(lambda ban: self.get_banned_word_text(ban, current_time), banned_words))