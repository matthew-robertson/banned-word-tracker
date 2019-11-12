from confusables import confusable_regex
import datetime
import json
import re
import requests

from config import API_BASE_URL, CLIENT_KEY

class BanInstance:
  def __init__(self, banJson, current_time, timeout_duration, session=requests.Session()):
    self._session = session
    self.ban_id = banJson['rowid']
    self.banned_word = banJson['banned_word']
    self.calledout_at = datetime.datetime.strptime(banJson['calledout_at'], "%Y-%m-%d %H:%M:%S")
    self.infracted_at = datetime.datetime.strptime(banJson['infracted_at'], "%Y-%m-%d %H:%M:%S")
    self.server_id = banJson['server_id']

    self.is_cooldown_active = (current_time - self.calledout_at).total_seconds() < timeout_duration
    self.timeout_expiration_time = self.calledout_at + datetime.timedelta(seconds=timeout_duration)

  def set_word(self, new_word):
    response = self._session.post(
      API_BASE_URL + 'v1/servers/' + str(self.server_id) + '/bans/' + str(self.ban_id) , 
      headers = {'Authorization': 'Bot ' + CLIENT_KEY},
      json = {'banned_word': new_word})

    if (response.ok):
      jData = json.loads(response.content)
      self.banned_word = jData['banned_word']
      self.calledout_at = datetime.datetime.strptime(jData['calledout_at'], "%Y-%m-%d %H:%M:%S")
      self.infracted_at = datetime.datetime.strptime(jData['infracted_at'], "%Y-%m-%d %H:%M:%S")

  def send_infringing_message(self, current_time, called_out):
    requestData = {'ban_id': self.ban_id, 'sent_time': current_time.strftime("%Y-%m-%d %H:%M:%S")}
    if called_out:
      requestData['called_out'] = True

    response = self._session.post(
      API_BASE_URL + 'v1/messages', 
      headers = {'Authorization': 'Bot ' + CLIENT_KEY},
      json = requestData)
    
    if (response.ok):
      jData = json.loads(response.content)
      self.banned_word = jData['banned_word']
      self.calledout_at = datetime.datetime.strptime(jData['calledout_at'], "%Y-%m-%d %H:%M:%S")
      self.infracted_at = datetime.datetime.strptime(jData['infracted_at'], "%Y-%m-%d %H:%M:%S")

  def check_if_message_infringes(self, message):
    word_boundary_chars = '(?:^|$|\\s|\\b)'
    pattern = word_boundary_chars + confusable_regex(self.banned_word, True) + word_boundary_chars
    if re.search(pattern, message) is not None:
      return True
    return False