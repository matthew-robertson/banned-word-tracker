import datetime

class ServerDao:

  def __init__(self, connection):
    self.conn = connection

  def get_all_servers(self):
    c = self.conn.cursor()
    c.execute('SELECT * FROM `server`')

    return c.fetchall()

  def get_server(self, server_id):
    c = self.conn.cursor()
    c.execute('SELECT server_id, infracted_at, calledout_at, awake, timeout_duration_seconds FROM `server` WHERE server_id='+str(server_id))

    row = c.fetchone()
    if row is None:
      return None

    server = {
      'server_id': row[0], 
      'infracted_at': datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"), 
      'calledout_at': datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S"), 
      'awake': row[3],
      'timeout_duration_seconds': row[4]
    }
    return server

  def get_banned_words_for_server(self, server_id):
    c = self.conn.cursor()
    c.execute('SELECT rowid, server_id, banned_word, infracted_at, calledout_at FROM `server_banned_word` WHERE server_id='+str(server_id))

    rows = c.fetchall()
    words = list(map(lambda row: {
      'rowid': row[0],
      'server_id': row[1],
      'banned_word': row[2],
      'infracted_at': datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S"),
      'calledout_at': datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S"),
      }, rows))
    return words

  def insert_server(self, server_row):
    c = self.conn.cursor()
    res = c.execute('INSERT OR REPLACE INTO `server` (server_id, infracted_at, calledout_at, awake, timeout_duration_seconds) VALUES (?, ?, ?, ?, ?)',
            (server_row['server_id'],
             server_row['infracted_at'].strftime("%Y-%m-%d %H:%M:%S"),
             server_row['calledout_at'].strftime("%Y-%m-%d %H:%M:%S"),
             int(server_row['awake']),
             server_row['timeout_duration_seconds']))
    self.conn.commit()

    return res


  def insert_multiple_words(word_rows):
    for row in word_rows:
      insert_banned_word(row)


  def insert_banned_word(self, word_row):
    c = self.conn.cursor()
    res = c.execute('INSERT OR REPLACE INTO `server_banned_word` (row_id, server_id, banned_word, infracted_at, calledout_at) VALUES (?, ?, ?, ?, ?)',
            (word_row['rowid'],
             word_row['server_id'],
             word_row['banned_word']
             word_row['infracted_at'].strftime("%Y-%m-%d %H:%M:%S"),
             word_row['calledout_at'].strftime("%Y-%m-%d %H:%M:%S"),
    self.conn.commit()

    return res
