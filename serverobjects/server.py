import requests
import json
import os

from serverobjects import BanInstance

API_BASE_URL = os.environ["API_BASE_URL"]
CLIENT_KEY = os.environ["CLIENT_KEY"]

class DiscordServer:
	def __init__(self, server_data, current_time, session):
		self._session = session
		self.current_time = current_time
		self.server_id = int(server_data['server_id'])
		self.awake = bool(server_data['awake'])
		self.timeout_duration_seconds = int(server_data['timeout_duration_seconds'])
		self.banned_words = []
		for word in server_data['banned_words']:
			ban = BanInstance(word, self.current_time, self.timeout_duration_seconds, self._session)
			self.banned_words.append(ban)

	def set_awake(self, new_awake):
		self.update_server_settings({'awake': new_awake})

	def set_timeout(self, new_timeout):
		self.update_server_settings({'timeout_duration_seconds': new_timeout})

	def update_server_settings(self, updated_params):
		response = self._session.post(
			API_BASE_URL + 'v1/servers/' + str(self.server_id), 
			json = updated_params)

		if response.ok:
			jData = json.loads(response.content)
			self.awake = bool(jData['awake'])
			self.timeout_duration_seconds = int(jData['timeout_duration_seconds'])
			return True
		return False

	def ban_new_word(self, new_word):
		response = self._session.post(
			API_BASE_URL + 'v1/servers/' + str(self.server_id) + '/bans',
			json = {'banned_word': new_word})

		if response.ok:
			new_ban = BanInstance(json.loads(response.content), self.current_time, self.timeout_duration_seconds, self._session)
			self.banned_words.append(new_ban)
		return response.ok

	def unban_word(self, index_to_unban):
		ban_to_remove = self.banned_words[index_to_unban]
		response = self._session.delete(
			API_BASE_URL + 'v1/servers/' + str(self.server_id) + '/bans/' + str(ban_to_remove.ban_id))

		if response.ok:
			return ban_to_remove.banned_word
		return ""