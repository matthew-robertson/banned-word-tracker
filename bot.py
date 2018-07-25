import discord
import asyncio
import re
import datetime
import math

# A pattern to match the word vore, and only the single word vore.
pattern = re.compile(r'\b[V|v][O|Ò|Ó|Ô|Õ|Ö|o|ò|ó|ô|õ|ö][R|r][E|È|É|Ê|Ë|e|è|é|ê|ë][S|s]?\b')
serverAndDate = {}
botStartup = datetime.datetime.now()
lastMention = {}
awake = {}

client = discord.Client()

def readTimesFromFile():
    global serverAndDate
    with open("timeStamps.txt", "r") as target:
        for line in target:
            tmp = line.split(',')
            tmp[1] = tmp[1][0:-1]
            serverAndDate[tmp[0]] = datetime.datetime.strptime(tmp[1], "%Y-%m-%d %H:%M:%S")
            if (len(tmp) >= 3):
                awake[tmp[0]] = bool(tmp[2])
            else:
                awake[tmp[0]] = True
            

def writeTimesToFile():
    with open('timeStamps.txt', 'w') as target:
        for serverId in serverAndDate:
            target.write('{},{},{}\n'.format(serverId, serverAndDate[serverId].strftime("%Y-%m-%d %H:%M:%S"), awake[serverId]))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    global botStartup
    global serverAndDate
    global lastMention
    global awake
    currentTime = datetime.datetime.now()
    serverId = message.server.id
    
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
    if serverId in serverAndDate:
        lastReferenced = serverAndDate[serverId]
    if serverId not in lastMention:
        bot = None
        for x in message.server.members:
            if client.user.id == x.id:
                bot = x
                break
        lastMention[serverId] = bot.joined_at
    if serverId not in awake:
        awake[serverId] = True

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

    if (hasattr(message.author, 'server_permissions')):
        permission = message.author.server_permissions
        if message.content.startswith('!vtsilence') and permission.administrator:
            await client.send_message(message.channel, "Ok {}, I'll be quiet now. use '!vtalert' to wake me back up!".format(message.author.mention))
            awake[serverId] = False
            writeTimesToFile()
        elif message.content.startswith('!vtalert') and permission.administrator:
            await client.send_message(message.channel, "Ok {}, I'm scanning now.".format(message.author.mention))
            awake[serverId] = True
            writeTimesToFile()
    if message.content.startswith('!vtsilence') or message.content.startswith('!vtalert'):
        pass
    elif message.content.startswith('!vthelp'):
        await client.send_message(message.channel, "You can ask me how long we've made it with '!vt'.\n If you're an admin you can silence me with '!vtsilence' and wake me back up with '!vtalert'")
    elif message.content.startswith('!vt'):
        await client.send_message(message.channel, 'The server has gone {}{}{}{} without mentioning the forbidden word.'.format(dt, ht, mt, st))
    if ((pattern.search(message.content) is not None) and (message.author.id != client.user.id)):
        serverAndDate[serverId] = currentTime
        writeTimesToFile()
        print ("{}::: {} lasted {} seconds.".format(currentTime, serverId, (currentTime - lastMention[serverId]).total_seconds()))
        if (awake[serverId] and (currentTime - lastMention[serverId]).total_seconds() >= 1800):
            await client.send_message(message.channel, '{} referenced the forbidden word, setting the counter back to 0. I\'ll wait a half hour before warning you again.\n The server went {}{}{}{} without mentioning it.'.format(message.author.mention, dt, ht, mt, st))
            lastMention[serverId] = currentTime


readTimesFromFile()
print('Stored server info:')
count = 0
for id in serverAndDate:
    print ("{}: id: {}, time: {}".format(count, id, serverAndDate[id]))
    count = count + 1

with open("key.txt", "r") as target:
        for line in target:
            client.run(line)