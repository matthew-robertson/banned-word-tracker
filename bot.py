import asyncio
import datetime
import discord
from enum import Enum
import json
import requests
import time

from config import API_BASE_URL
from serverobjects.server import DiscordServer
from utils.time import parse_time, format_time, format_seconds
from commands import CooldownCommand, HelpCommand, TimerCommand, SilenceCommand, AlertCommand, ChangeBanCommand, ChangeTimeCommand

class Commands(Enum):
    NEEDADMIN = -1
    NOCOMMAND = 0
    VTSILENCE = 1
    VTALERT   = 2
    VTHELP    = 3
    VT        = 4
    VTLAST    = 5
    VTCT      = 6
    VTDELAY   = 7
    VTBAN     = 8

def fetch_server_from_api(server_id, current_time, session):
    response = session.get(API_BASE_URL + 'v1/servers/' + str(server_id))

    if (not response.ok):
        response = session.post(
            API_BASE_URL + 'v1/servers', 
            json = {'server_id': server_id})
    
    if (response.ok):
        jData = json.loads(response.content)
        return DiscordServer(jData, current_time, session)

# Only returns a command if the command is in the message and also valid
def parse_for_command(msg, msg_author, channel):
    # Check if any admin only commands have been entered
    if (hasattr(msg_author, 'permissions_in')):
        permission = msg_author.permissions_in(channel)
        if msg.startswith('!vtsilence') and permission.administrator:
            return Commands.VTSILENCE            
        elif msg.startswith('!vtalert') and permission.administrator:
            return Commands.VTALERT
        elif msg.startswith('!vtdelay') and permission.administrator:
            return Commands.VTDELAY
        elif msg.startswith('!vtban') and permission.administrator:
            return Commands.VTBAN

    # Check the other commands
    if msg.startswith('!vtsilence') or msg.startswith('!vtalert') or msg.startswith('!vtdelay') or msg.startswith('!vtban'):
        return Commands.NEEDADMIN
    elif msg.startswith('!vthelp'):
        return Commands.VTHELP
    elif msg.startswith('!vtlast'):
        return Commands.VTLAST
    elif msg.startswith('!vtct'):
        return Commands.VTCT
    elif msg.startswith('!vt'):
        return Commands.VT

    return Commands.NOCOMMAND

def handle_vtsilence(current_server, msg_author):
    return SilenceCommand().execute(current_server, None, None, msg_author)

def handle_vtalert(current_server, msg_author):
    return AlertCommand().execute(current_server, None, None, msg_author)

def handle_vtban(current_server, message, msg_author):
    return ChangeBanCommand().execute(current_server, None, message, msg_author)

def handle_vtdelay(current_server, message):
    return ChangeTimeCommand().execute(current_server, None, message, None)

def handle_vtct(current_time, current_server):
    return CooldownCommand().execute(current_server, current_time)

def handle_vthelp():
    return HelpCommand().execute()

def handle_vt(current_time, current_server):
   return TimerCommand().execute(current_server, current_time)

def handle_command(found_command, current_time, current_server, message):
    msg_to_send = ""
    if found_command is Commands.VTSILENCE:
        msg_to_send = handle_vtsilence(current_server, message.author)
    elif found_command is Commands.VTALERT:
        msg_to_send = handle_vtalert(current_server, message.author)
    elif found_command is Commands.VTDELAY:
        msg_to_send = handle_vtdelay(current_server, message.content)
    elif found_command is Commands.VTBAN:
        msg_to_send = handle_vtban(current_server, message.content, message.author)
    elif found_command is Commands.VTCT:
        msg_to_send = handle_vtct(current_time, current_server)
    elif found_command is Commands.VTHELP:
        msg_to_send = handle_vthelp()
    elif found_command is Commands.VTLAST:
        msg_to_send = "Sorry, this has been removed. Try '!vtct' instead."
    elif found_command is Commands.VT:
        msg_to_send = handle_vt(current_time, current_server)

    return msg_to_send

def handle_detected_banned_word(current_time, current_server, message, banned_word):
    time_lasted = format_time(current_time, banned_word.infracted_at)
    timeout_length = format_seconds(current_server.timeout_duration_seconds)
    tDiff = current_time - banned_word.infracted_at

    msg_to_send = ""
    called_out = False
    if (current_server.awake and not banned_word.is_cooldown_active):
        called_out = True
        msg_to_send = "{} referenced a forbidden word, setting its counter back to 0.\n".format(message.author.mention)
        msg_to_send += "I'll wait {} before warning you for this word again.\n".format(timeout_length)
        msg_to_send += "The server went {} without mentioning the forbidden word '{}'.".format(time_lasted, banned_word.banned_word)

    banned_word.send_infringing_message(current_time, called_out)
    print("{}::: {} lasted {} seconds.".format(current_time, current_server.server_id, (tDiff).total_seconds()))
    return msg_to_send

def handle_message(message, current_time, session):
    if not message.guild or message.author.bot:
        return ""

    server_id = message.guild.id
    current_server = fetch_server_from_api(server_id, current_time, session)

    found_command = parse_for_command(message.content, message.author, message.channel)
    msg_to_send = handle_command(found_command, current_time, current_server, message)

    # Check if they've said the forbidden word
    banned_word_msg = ""
    if not found_command is Commands.VTBAN:
        for banned_word in current_server.banned_words:
            contains_banned_word = banned_word.check_if_message_infringes(message.content)
            if contains_banned_word:
                temp_msg = handle_detected_banned_word(current_time, current_server, message, banned_word)
                if len(banned_word_msg):
                    banned_word_msg += "\n"
                banned_word_msg += temp_msg

    if len(msg_to_send) and len(banned_word_msg):
        msg_to_send += "\n"
    return msg_to_send + banned_word_msg

def run_bot(shard_id, shard_count, client_key, session):
    client = discord.Client(shard_id=shard_id, shard_count=shard_count)

    @client.event
    async def on_ready():
        print("Logged in as")
        print(client.user.name)
        print(client.user.id)
        print("On {} servers".format(len(client.guilds)))
        print("------")
        await client.change_presence(activity = discord.Game(name = 'Use !vthelp'))

    @client.event
    async def on_message_edit(before, message):
        msg_to_send = handle_message(message, datetime.datetime.now(), session)    
        if len(msg_to_send):
            await message.channel.send(msg_to_send)

    @client.event
    async def on_message(message):
        msg_to_send = handle_message(message, datetime.datetime.now(), session)    
        if msg_to_send:
            await message.channel.send(msg_to_send)

    client.run(client_key)
