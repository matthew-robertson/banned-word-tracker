from abc import ABC, abstractmethod

class Command(ABC):
	def is_command_authorized(self, permissions=None):
		return True

	@abstractmethod
	def execute(self, current_server, current_time, message, author):
		pass