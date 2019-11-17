from commands.command import Command

class AlertCommand(Command):
	def is_command_authorized(self, permissions=None):
		return permissions and permissions.administrator

	def execute(self, current_server, current_time=None, message=None, author=None):
		msg_to_send = "Ok {}, I'm scanning now.".format(author.mention)
		current_server.set_awake(True)
		return msg_to_send