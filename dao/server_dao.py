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
    c.execute('SELECT * FROM `server` WHERE server_id='+str(server_id))

    row = c.fetchone()
    if row is None:
      return None

    server = {
      'server_id': row[0], 
      'infracted_at': datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"), 
      'calledout_at': datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S"), 
      'awake': row[3]
    }
    return server

  def insert_server(self, server_row):
    c = self.conn.cursor()
    res = c.execute('INSERT OR REPLACE INTO `server` (server_id, infracted_at, calledout_at, awake) VALUES (?, ?, ?, ?)',
            (server_row['server_id'], server_row['infracted_at'].strftime("%Y-%m-%d %H:%M:%S"),
             server_row['calledout_at'].strftime("%Y-%m-%d %H:%M:%S"), int(server_row['awake'])))
    self.conn.commit()

    return res
