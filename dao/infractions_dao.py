from dao import conn

class InfractionsDao:

  def get_all_infractions():
    c = conn.cursor()
    c.execute('SELECT * FROM `server`')

    return c.fetchall()

  def insert_infraction(server_id, infracted_at, awake):
    c = conn.cursor()
    res = c.execute('INSERT OR REPLACE INTO `server` (server_id, infracted_at, awake) VALUES (?, ?, ?)', (server_id, infracted_at, int(awake)))
    conn.commit()

    return res
