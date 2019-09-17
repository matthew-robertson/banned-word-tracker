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
    c.execute('SELECT server_id, awake, timeout_duration_seconds FROM `server` WHERE server_id='+str(server_id))

    row = c.fetchone()
    if row is None:
      return None

    server = {
      'server_id': row[0], 
      'awake': row[1],
      'timeout_duration_seconds': row[2]
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
    res = c.execute('INSERT OR REPLACE INTO `server` (server_id, awake, timeout_duration_seconds, calledout_at, infracted_at) VALUES (?, ?, ?, ?, ?)',
            (server_row['server_id'],
             int(server_row['awake']),
             server_row['timeout_duration_seconds'],
             "-1",
             "-1"))
    self.conn.commit()

    return res


  def update_multiple_words(word_rows):
    for row in word_rows:
      update_banned_word(row)


  def update_banned_word(self, word_row):
    c = self.conn.cursor()
    res = c.execute("UPDATE `server_banned_word` SET banned_word=?, infracted_at=?, calledout_at=? WHERE rowid=? AND server_id=?",
            (word_row['banned_word'],
             word_row['infracted_at'].strftime("%Y-%m-%d %H:%M:%S"),
             word_row['calledout_at'].strftime("%Y-%m-%d %H:%M:%S"),
             word_row['rowid'],
             word_row['server_id']))
    self.conn.commit()

    return res

  def insert_default_banned_word(self, server_id, join_time):
    c = self.conn.cursor()
    res = c.execute('INSERT INTO `server_banned_word` (server_id, banned_word, infracted_at, calledout_at) VALUES (?, ?, ?, ?)',
            (server_id,
             'defaultbannedword',
             join_time.strftime("%Y-%m-%d %H:%M:%S"),
             (join_time - datetime.timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M:%S")))
    self.conn.commit()

    return res