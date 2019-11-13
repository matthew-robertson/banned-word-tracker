import asyncio
import datetime
import discord
from enum import Enum
import json
import math
import requests
import time

from config import API_BASE_URL
from serverobjects.server import DiscordServer

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

def parse_time(time_string):
    splits = time_string.strip().split(':')
    if not is_valid_time(splits):
        return -1

    second_total = int(splits[-1])
    if len(splits) >= 2:
        second_total += int(splits[-2]) * 60
    if len(splits) >= 3:
        second_total += int(splits[-3]) * 60 * 60

    return second_total

def is_valid_time(time_splits):
    return all(split.isnumeric() for split in time_splits) and len(time_splits) <= 3

def format_seconds(seconds_count):
    current_time = datetime.datetime.now()
    return format_time(current_time, current_time - datetime.timedelta(seconds=seconds_count))

def format_time(current_time, pastTime):
    diff = current_time - pastTime
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
    msg_to_send = "Ok {}, I'll be quiet now. use '!vtalert' to wake me back up!".format(msg_author.mention)
    current_server.set_awake(False)
    return msg_to_send

def handle_vtalert(current_server, msg_author):
    msg_to_send = "Ok {}, I'm scanning now.".format(msg_author.mention)
    current_server.set_awake(True)
    return msg_to_send

def handle_vtban(current_server, new_word, msg_author):
    if len(new_word) < 1:
        return "Sorry, I can't ban the empty string. Please try a message of the form '!vtban [wordToBan]'"

    current_server.banned_words[0].set_word(new_word)
    msg_to_send = "Ok {}, '{}' is now considered a forbidden word.".format(msg_author.mention, new_word)
    return msg_to_send

def handle_vtdelay(current_server, time_string):
    parsed_time = parse_time(time_string)

    if parsed_time >= 0:
        current_server.set_timeout(parsed_time)
        formatted_time = format_seconds(parsed_time)
        return "Cool, from now on I'll wait at least {} between alerts.".format(formatted_time)
    else:
        return "Sorry, I don't understand that formatting. I was expecting something like '!vtct hh:mm:ss'"

def handle_vtct(current_time, current_server):
    timeout_length = format_seconds(current_server.timeout_duration_seconds)
    msg_to_send = "The cooldown period is {}.".format(timeout_length)

    for banned_word in current_server.banned_words:
        timeoutRemaining = format_time(banned_word.timeout_expiration_time, current_time)
        if banned_word.is_cooldown_active:
            msg_to_send += "\nI'll be able to issue another alert for '{}' in {}.".format(banned_word.banned_word, timeoutRemaining)
        else:
            msg_to_send += "\nI'm ready to issue another warning for '{}' now.".format(banned_word.banned_word)

    return msg_to_send

def handle_vthelp():
    msg_to_send = "You can ask me how long we've made it with '!vt'.\n"
    msg_to_send += "You can learn how long my timeout is set for, and when I can issue another warning with '!vtct'.\n"
    msg_to_send += "For other commands, server management, and general help, please check either the documentation (https://bwbdiscord.gitbook.io/banned-word-tracker/) or the support server (https://discord.gg/nUZsfYS)."
    return msg_to_send

def handle_vtlast(current_time, current_server):
    banned_words = current_server.banned_words
    time_without_warning = format_time(current_time, banned_words[0].calledout_at)
    msg_to_send = "The server last received a warning for '{}' {} ago.".format(banned_words[0].banned_word, time_without_warning)

    for banned_word in banned_words[1:]:
        time_without_warning = format_time(current_time, banned_word.calledout_at)
        msg_to_send += "\nThe server last received a warning for '{}' {} ago.".format(banned_word.banned_word, time_without_warning)

    return msg_to_send

def handle_vt(current_time, current_server):
    banned_words = current_server.banned_words
    timeLasted = format_time(current_time, banned_words[0].infracted_at)
    msg_to_send = "The server has gone {} without mentioning '{}'.".format(timeLasted, banned_words[0].banned_word)
    for banned_word in banned_words[1:]:
        timeLasted = format_time(current_time, banned_word.infracted_at)
        msg_to_send += "\nThe server has gone {} without mentioning '{}'.".format(timeLasted, banned_word.banned_word)

    return msg_to_send

def handle_command(found_command, current_time, current_server, message):
    msg_to_send = ""
    if found_command is Commands.VTSILENCE:
        msg_to_send = handle_vtsilence(current_server, message.author)
    elif found_command is Commands.VTALERT:
        msg_to_send = handle_vtalert(current_server, message.author)
    elif found_command is Commands.VTDELAY:
        msg_to_send = handle_vtdelay(current_server, message.content[8:])
    elif found_command is Commands.VTBAN:
        new_word = message.content[6:].lstrip().split(' ')[0]
        msg_to_send = handle_vtban(current_server, new_word, message.author)
    elif found_command is Commands.VTCT:
        msg_to_send = handle_vtct(current_time, current_server)
    elif found_command is Commands.VTHELP:
        msg_to_send = handle_vthelp()
    elif found_command is Commands.VTLAST:
        msg_to_send = handle_vtlast(current_time, current_server)
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
