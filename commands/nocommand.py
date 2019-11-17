from commands.command import Command

class NoCommand(Command):
	def execute(self, current_server, current_time, message, author):
		return ""