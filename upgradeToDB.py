import datetime
import sqlite3

import config
from dao.server_dao import ServerDao

conn = sqlite3.connect(config.DB_LOCATION)
server_dao = ServerDao(conn)

with open("timeStamps.txt", "r") as target:
    for line in target:
        currentServer = {}
        tmp = line.split(',')
        tmp[1] = tmp[1][0:-1]

        currentServer['server_id'] = tmp[0]
        currentServer['infracted_at'] = datetime.datetime.strptime(tmp[1], "%Y-%m-%d %H:%M:%S")
        currentServer['calledout_at'] = currentServer['infracted_at']
        if (len(tmp) >= 3):
            currentServer['awake'] = tmp[2].strip() == 'True'
        else:
            currentServer['awake'] = True

        server_dao.insert_server(currentServer)