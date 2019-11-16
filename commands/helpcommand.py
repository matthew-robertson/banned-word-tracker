from commands.command import Command

class HelpCommand(Command):
	def execute(self, current_server=None, current_time=None, message=None, author=None):
		msg_to_send = "You can ask me how long we've made it with '!vt'.\n"
		msg_to_send += "You can learn how long my timeout is set for, and when I can issue another warning with '!vtct'.\n"
		msg_to_send += "For other commands, server management, and general help, please check either the documentation (https://bwbdiscord.gitbook.io/banned-word-tracker/) or the support server (https://discord.gg/W7mrxRd)."
		return msg_to_send