import requests
import json

from config import API_BASE_URL, CLIENT_KEY
from serverobjects.ban import BanInstance

class DiscordServer:
	def __init__(self, server_data, current_time, session=requests.Session()):
		self._session = session
		self.server_id = int(server_data['server_id'])
		self.awake = bool(server_data['awake'])
		self.timeout_duration_seconds = int(server_data['timeout_duration_seconds'])
		self.banned_words = []
		for word in server_data['banned_words']:
			ban = BanInstance(word, current_time, self.timeout_duration_seconds, self._session)
			self.banned_words.append(ban)

	def set_awake(self, new_awake):
		self.update_server_settings({'awake': new_awake})

	def set_timeout(self, new_timeout):
		self.update_server_settings({'timeout_duration_seconds': new_timeout})

	def update_server_settings(self, updated_params):
		response = self._session.post(
			API_BASE_URL + 'v1/servers/' + str(self.server_id), 
			headers = {'Authorization': 'Bot ' + CLIENT_KEY},
			json = updated_params)

		if (response.ok):
			jData = json.loads(response.content)
			self.awake = bool(jData['awake'])
			self.timeout_duration_seconds = int(jData['timeout_duration_seconds'])