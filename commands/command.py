from abc import ABC, abstractmethod

class Command(ABC):
	def __init__(self):
		self.detect_bans_in_message = True

	def is_command_authorized(self, permissions=None):
		return True

	@abstractmethod
	def execute(self, current_server, current_time, message, author):
		pass