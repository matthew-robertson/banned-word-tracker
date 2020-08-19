from commands.command import Command

class ChangePrefixCommand(Command):
	def is_command_authorized(self, permissions=None):
		return permissions and permissions.administrator

	def execute(self, current_server, current_time, message, author):
		new_prefix = message.lstrip().split(' ')[1]
		print(new_prefix)
		print("!!!!!!!!!!!!!")
		if len(new_prefix) > 0 and len(new_prefix) <= 10:
			update_succeeded = current_server.set_prefix(new_prefix)
			if not update_succeeded:
				return "Sorry, something went wrong and I couldn't update the prefix."
			return "Cool, from now on you'll need to start a message with '{}' for me to treat it as a command.".format(new_prefix)
		else:
			return "Sorry, I don't understand that formatting. I was expecting a new prefix between 1 and 10 characters long."