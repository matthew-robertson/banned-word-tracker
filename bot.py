import asyncio
import datetime
import discord
from enum import Enum
import math
import re
import sys
import time

from dao.server_dao import ServerDao

# A pattern to match the word vore, and only the single word vore.
pattern = re.compile(r'\b[\*|_|~|`|-|\.]*[V|v][\*|_|~|`|-|\.]*[O|Ò|Ó|Ô|Õ|Ö|o|ò|ó|ô|õ|ö|ᴑ|о][\*|_|~|`|-|\.]*[R|r][\*|_|~|`|-|\.]*[E|È|É|Ê|Ë|Е|e|è|é|ê|ë|е][\*|_|~|`|-|\.]*[S|s]?\b')
client = discord.Client(shard_id=int(sys.argv[1]), shard_count=int(sys.argv[2]))

class Commands(Enum):
    NOCOMMAND = 0
    VTSILENCE = 1
    VTALERT   = 2
    VTHELP    = 3
    VT        = 4

def format_time(currentTime, lastReferenced):
    diff = currentTime - lastReferenced
    hours = math.floor(diff.seconds/3600)
    minutes = math.floor((diff.seconds - hours*3600)/60)
    seconds = diff.seconds - hours*3600 - minutes*60
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

    return dt+ht+mt+st

# Only returns a command if the command is in the message and also valid
def parse_for_command(msg, msg_author):
    # Check if any admin only commands have been entered
    if (hasattr(msg_author, 'server_permissions')):
        permission = msg_author.server_permissions
        if msg.startswith('!vtsilence') and permission.administrator:
            return Commands.VTSILENCE            
        elif msg.startswith('!vtalert') and permission.administrator:
            return Commands.VTALERT

    # Check the other commands
    if msg.startswith('!vtsilence') or msg.startswith('!vtalert'):
        pass
    elif msg.startswith('!vthelp'):
        return Commands.VTHELP
    elif msg.startswith('!vt'):
        return Commands.VT

def handle_message(message, botID):
    msg_to_send = False
    currentTime = datetime.datetime.now()
    if not message.server:
        return msg_to_send

    serverId = message.server.id
    currentServer = ServerDao.get_server(serverId)
    if currentServer is None:
        currentServer = {}
        currentServer['server_id'] = serverId
        bot = None
        for x in message.server.members:
            if botID == x.id:
                bot = x
                break
        currentServer['infracted_at'] = bot.joined_at
        currentServer['calledout_at'] = bot.joined_at
        currentServer['awake'] = True
        ServerDao.insert_server(currentServer)

    timeLasted = format_time(currentTime, currentServer['infracted_at'])

    foundCommand = parse_for_command(message.content, message.author)
    if foundCommand is Commands.VTSILENCE:
        msg_to_send = "Ok {}, I'll be quiet now. use '!vtalert' to wake me back up!".format(message.author.mention)
        currentServer['awake'] = False
        ServerDao.insert_server(currentServer)
    elif foundCommand is Commands.VTALERT:
        msg_to_send = "Ok {}, I'm scanning now.".format(message.author.mention)
        currentServer['awake'] = True
        ServerDao.insert_server(currentServer)
    elif foundCommand is Commands.VTHELP:
        msg_to_send = "You can ask me how long we've made it with '!vt'.\n If you're an admin you can silence me with '!vtsilence' and wake me back up with '!vtalert'"
    elif foundCommand is Commands.VT:
        msg_to_send = "The server has gone {} without mentioning the forbidden word.".format(timeLasted)

    # Check if they've said the forbidden word
    if ((pattern.search(message.content) is not None) and (message.author.id != botID)):
        currentServer['infracted_at'] = currentTime
        
        if (currentServer['awake'] and (currentTime - currentServer['calledout_at']).total_seconds() >= 1800):
            currentServer['calledout_at'] = currentTime
            msg_to_send = "{} referenced the forbidden word, setting the counter back to 0. I'll wait a half hour before warning you again.\n The server went {} without mentioning it.".format(message.author.mention, timeLasted)

        ServerDao.insert_server(currentServer)
        print("{}::: {} lasted {} seconds.".format(currentTime, serverId, (currentTime - currentServer['infracted_at']).total_seconds()))

    return msg_to_send

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

@client.event
async def on_message_edit(before, message):
    msg_to_send = handle_message(message, client.user.id)    
    if msg_to_send:
        await client.send_message(message.channel, msg_to_send)

@client.event
async def on_message(message):
    msg_to_send = handle_message(message, client.user.id)    
    if msg_to_send:
        await client.send_message(message.channel, msg_to_send)

while True:
    try:
        with open("key.txt", "r") as target:
            for line in target:
                line = line.strip()
                client.run(line)
    except BaseException:
            time.sleep(5)