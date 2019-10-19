import datetime
import requests
import json

from config import API_BASE_URL, CLIENT_KEY

class ServerDao:
  def get_server(self, server_id):
    response = requests.get(
      API_BASE_URL + 'v1/servers/' + str(server_id),
      headers = {'Authorization': 'Bot ' + CLIENT_KEY})
    
    if (response.ok):
      jData = json.loads(response.content)
      server = {
        'server_id': server_id, 
        'awake': bool(jData['awake']),
        'timeout_duration_seconds': int(jData['timeout_duration_seconds'])
      }
      return server
    else:
      return None

  def get_banned_words_for_server(self, server_id):
    response = requests.get(
      API_BASE_URL + 'v1/servers/' + str(server_id) + '/bans',
      headers = {'Authorization': 'Bot ' + CLIENT_KEY})

    if (response.ok):
      jData = json.loads(response.content)
      words = list(map(lambda row: {
        'rowid': int(row['rowid']),
        'server_id': server_id,
        'banned_word': row['banned_word'],
        'infracted_at': datetime.datetime.strptime(row['infracted_at'], "%Y-%m-%d %H:%M:%S"),
        'calledout_at': datetime.datetime.strptime(row['calledout_at'], "%Y-%m-%d %H:%M:%S"),
        }, jData))
      return words
    else:
      return None

  def update_server(self, server_id, updated_params):
    response = requests.post(
      API_BASE_URL + 'v1/servers/' + str(server_id), 
      headers = {'Authorization': 'Bot ' + CLIENT_KEY},
      json = updated_params)

    if (response.ok):
      return json.loads(response.content)
    return None

  def insert_default_server(self, server_id):
    response = requests.post(
      API_BASE_URL + 'v1/servers', 
      headers = {'Authorization': 'Bot ' + CLIENT_KEY},
      json = {'server_id': server_id})
    
    if (response.ok):
      return json.loads(response.content)
    return None

  def update_multiple_words(word_rows):
    for row in word_rows:
      update_banned_word(row)


  def update_banned_word(self, word_row):
    response = requests.post(
      API_BASE_URL + 'v1/servers/' + str(word_row['server_id']) + '/bans/' + str(word_row['rowid']) , 
      headers = {'Authorization': 'Bot ' + CLIENT_KEY},
      json = {'banned_word': word_row['banned_word']})
    
    if (response.ok):
      return json.loads(response.content)
    return None

  def send_infringing_message(self, ban_id, called_out):
    requestData = {'ban_id': ban_id, 'sent_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if called_out:
      requestData['called_out'] = True

    response = requests.post(
      API_BASE_URL + 'v1/messages', 
      headers = {'Authorization': 'Bot ' + CLIENT_KEY},
      json = requestData)
    
    if (response.ok):
      return json.loads(response.content)
    return None