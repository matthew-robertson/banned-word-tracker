import discord
import asyncio
import re
import datetime
import math

# A pattern to match the word vore, and only the single word vore.
pattern = re.compile(r'\b[V|v][O|Ò|Ó|Ô|Õ|Ö|o|ò|ó|ô|õ|ö][R|r][E|È|É|Ê|Ë|e|è|é|ê|ë][S|s]?\b')
serverAndDate = {}
botStartup = datetime.datetime.now()
lastMention = datetime.datetime.now() - datetime.timedelta(days=1)
awake = True

client = discord.Client()

def readTimesFromFile():
    global serverAndDate
    with open("timeStamps.txt", "r") as target:
        for line in target:
            tmp = line.split(',')
            tmp[1] = tmp[1][0:-1]
            serverAndDate[tmp[0]] = datetime.datetime.strptime(tmp[1], "%Y-%m-%d %H:%M:%S")
            

def writeTimesToFile():
    with open('timeStamps.txt', 'w') as target:
        for serverId in serverAndDate:
            target.write('{},{}\n'.format(serverId, serverAndDate[serverId].strftime("%Y-%m-%d %H:%M:%S")))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    readTimesFromFile()
    print('Stored server info:')
    for id in serverAndDate:
        print ("id: {}, time: {}".format(id, serverAndDate[id]))

@client.event
async def on_message(message):
    global botStartup
    global serverAndDate
    global lastMention
    global awake
    currentTime = datetime.datetime.now()
    
    ''' I'm just using startup time instead of join date, because that makes way more sense for older
        servers if the filesystem stuff doesn't work
    '''
    #bot = None
    #for x in message.server.members:
    #    if client.user.id == x.id:
    #        bot = x
    #        break

    # Timezone hack, apparently isn't needed for Heroku.
    lastReferenced = botStartup
    if message.server.id in serverAndDate:
        lastReferenced = serverAndDate[message.server.id]

    # Begin time formatting
    diff = currentTime - lastReferenced
    hours = math.floor(diff.seconds/3600)
    minutes = math.floor((diff.seconds - hours * 3600)/60)
    seconds = diff.seconds - hours * 3600 - minutes * 60
    dt = "{} days, ".format(diff.days)
    ht = "{} hours, ".format(hours)
    mt = "{} minutes, and ".format(minutes)
    st = "{} seconds".format(seconds)

    if diff.days == 1:
        dt = "1 day, "
    elif diff.days == 0:
        dt = ""
        if hours == 0:
            ht = ""
            mt = "{} minutes and ".format(minutes)
            if minutes == 0:
                mt = ""

    if hours == 1:
        ht = "1 hour, "
    if minutes == 1:
        if ht == "":
            mt = "1 minute and "
        else:
            mt = "1 minute, and "
    if seconds == 1:
        st = "1 second"
    # End Time formatting stuff

    permission = message.author.server_permissions

    if message.content.startswith('!vtsilence') and permission.administrator:
        await client.send_message(message.channel, "Ok {}, I'll be quiet now. use '!vtalert' to wake me back up!".format(message.author.mention))
        awake = False
    elif message.content.startswith('!vtalert') and permission.administrator:
        await client.send_message(message.channel, "Ok {}, I'm scanning now.".format(message.author.mention))
        awake = True
    elif message.content.startswith('!vthelp'):
        await client.send_message(message.channel, "You can ask me how long we've made it with '!vt'.\n If you're an admin you can silence me with '!vtsilence' and wake me back up with '!vtalert'")
    elif message.content.startswith('!vt'):
        await client.send_message(message.channel, 'The server has gone {}{}{}{} without mentioning the forbidden word.'.format(dt, ht, mt, st))
    elif ((pattern.search(message.content) is not None) and (message.author.id != client.user.id)):
        serverAndDate[message.server.id] = currentTime
        writeTimesToFile()
        print((currentTime - lastMention).total_seconds())
        if (awake and (currentTime - lastMention).total_seconds() >= 1800):
            await client.send_message(message.channel, '{} referenced the forbidden word, setting the counter back to 0. I\'ll wait a half hour before warning you again.\n The server went {}{}{}{} without mentioning it.'.format(message.author.mention, dt, ht, mt, st))
            lastMention = currentTime

client.run('MzU1MTQ0NDUwNDM3MDIxNjk3.DJIlnQ.Yg56nQ6JdLbxUDmlkFnuu6ay2FM')