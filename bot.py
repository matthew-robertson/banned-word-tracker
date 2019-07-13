import asyncio
import datetime
import discord
from enum import Enum
import math
import re
import time

from dao.server_dao import ServerDao

# A pattern to match the word vore, and only the single word vore.
betweenStr = r'[\*_~|`\-\.]*'
pattern = re.compile(r'\b' + betweenStr +
                    r'[Vv]' + betweenStr +
                    r'[OÒÓÔÕÖoòóôõöᴑо]' + betweenStr +
                    r'[Rr]' + betweenStr +
                    r'[EÈÉÊËЕeèéêëе]' + betweenStr +
                    r'([Ss]|[Dd])?\b')

class Commands(Enum):
    NEEDADMIN = -1
    NOCOMMAND = 0
    VTSILENCE = 1
    VTALERT   = 2
    VTHELP    = 3
    VT        = 4
    VTLAST    = 5

def format_time(currentTime, pastTime):
    diff = currentTime - pastTime
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
    elif hours == 0:
        ht = ""

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
        return Commands.NEEDADMIN
    elif msg.startswith('!vthelp'):
        return Commands.VTHELP
    elif msg.startswith('!vtlast'):
        return Commands.VTLAST
    elif msg.startswith('!vt'):
        return Commands.VT

    return Commands.NOCOMMAND

def handle_message(server_dao, message, botID):
    if message.author.bot:
        return False

    msg_to_send = False
    currentTime = datetime.datetime.now()
    fromUTC = currentTime - datetime.datetime.utcnow()

    if not message.server:
        return msg_to_send

    serverId = message.server.id
    currentServer = server_dao.get_server(serverId)
    if currentServer is None:
        currentServer = {}
        currentServer['server_id'] = serverId
        bot = None
        for x in message.server.members:
            if botID == x.id:
                bot = x
                break


        currentServer['infracted_at'] = bot.joined_at + fromUTC
        currentServer['calledout_at'] = bot.joined_at + fromUTC - datetime.timedelta(minutes=60)
        currentServer['awake'] = True
        server_dao.insert_server(currentServer)

    timeLasted = format_time(currentTime, currentServer['infracted_at'])

    foundCommand = parse_for_command(message.content, message.author)
    if foundCommand is Commands.VTSILENCE:
        msg_to_send = "Ok {}, I'll be quiet now. use '!vtalert' to wake me back up!".format(message.author.mention)
        currentServer['awake'] = False
        server_dao.insert_server(currentServer)
    elif foundCommand is Commands.VTALERT:
        msg_to_send = "Ok {}, I'm scanning now.".format(message.author.mention)
        currentServer['awake'] = True
        server_dao.insert_server(currentServer)
    elif foundCommand is Commands.VTHELP:
        msg_to_send = "You can ask me how long we've made it with '!vt'.\nYou can learn how long it's been since my last warning with '!vtlast'.\nIf you're an admin you can silence me with '!vtsilence' and wake me back up with '!vtalert'"
    elif foundCommand is Commands.VTLAST:
        timeWithoutWarning = format_time(currentTime, currentServer['calledout_at'])
        msg_to_send = "The server last received a warning {} ago.".format(timeWithoutWarning)
    elif foundCommand is Commands.VT:
        msg_to_send = "The server has gone {} without mentioning the forbidden word.".format(timeLasted)

    # Check if they've said the forbidden word
    if pattern.search(message.content) is not None:
        tDiff = currentTime - currentServer['infracted_at']
        currentServer['infracted_at'] = currentTime
        
        if (currentServer['awake'] and (currentTime - currentServer['calledout_at']).total_seconds() >= 1800):
            currentServer['calledout_at'] = currentTime
            msg_to_send = "{} referenced the forbidden word, setting the counter back to 0. I'll wait a half hour before warning you again.\n The server went {} without mentioning it.".format(message.author.mention, timeLasted)

        server_dao.insert_server(currentServer)
        print("{}::: {} lasted {} seconds.".format(currentTime, serverId, (tDiff).total_seconds()))

    return msg_to_send

def run_bot(conn, shard_id, shard_count, client_key):
    client = discord.Client(shard_id=shard_id, shard_count=shard_count)
    server_dao = ServerDao(conn)

    @client.event
    async def on_ready():
        print("Logged in as")
        print(client.user.name)
        print(client.user.id)
        print("------")

    @client.event
    async def on_message_edit(before, message):
        msg_to_send = handle_message(server_dao, message, client.user.id)    
        if msg_to_send:
            await client.send_message(message.channel, msg_to_send)

    @client.event
    async def on_message(message):
        msg_to_send = handle_message(server_dao, message, client.user.id)    
        if msg_to_send:
            await client.send_message(message.channel, msg_to_send)

    client.run(client_key)
