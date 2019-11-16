from commands.command import Command

class SilenceCommand(Command):
	def is_command_authorized(self, permissions=None):
		return permissions and permissions.administrator

	def execute(self, current_server, current_time=None, message=None, author=None):
		msg_to_send = "Ok {}, I'll be quiet now. use '!vtalert' to wake me back up!".format(author.mention)
		current_server.set_awake(False)
		return msg_to_send