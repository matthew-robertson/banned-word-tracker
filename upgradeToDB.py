import datetime

from dao.server_dao import ServerDao

serverAndDate = {}
awake = {}
def readTimesFromFile():
    global serverAndDate
    with open("timeStamps.txt", "r") as target:
        for line in target:
            tmp = line.split(',')
            tmp[1] = tmp[1][0:-1]
            serverAndDate[tmp[0]] = datetime.datetime.strptime(tmp[1], "%Y-%m-%d %H:%M:%S")
            if (len(tmp) >= 3):
                awake[tmp[0]] = tmp[2].strip() == 'True'
            else:
                awake[tmp[0]] = True
    print (awake)
    print(serverAndDate)

def writeTimesToDB():
    for serverId in serverAndDate:
        ServerDao.insert_server(serverId, serverAndDate[serverId].strftime("%Y-%m-%d %H:%M:%S"), awake[serverId])

readTimesFromFile()
writeTimesToDB()