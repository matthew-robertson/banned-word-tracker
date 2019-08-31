import asyncio
import datetime
import discord
from enum import Enum
import math
import re
import time
from confusables import confusable_regex

from dao.server_dao import ServerDao

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
def parse_for_command(msg, msg_author):
    # Check if any admin only commands have been entered
    if (hasattr(msg_author, 'server_permissions')):
        permission = msg_author.server_permissions
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

def handle_vtsilence(server_dao, current_server, msg_author):
    msg_to_send = "Ok {}, I'll be quiet now. use '!vtalert' to wake me back up!".format(msg_author.mention)
    current_server['awake'] = False
    server_dao.insert_server(current_server)
    return msg_to_send

def handle_vtalert(server_dao, current_server, msg_author):
    msg_to_send = "Ok {}, I'm scanning now.".format(msg_author.mention)
    current_server['awake'] = True
    server_dao.insert_server(current_server)
    return msg_to_send

def handle_vtban(server_dao, current_time, banned_words, new_word, msg_author, timeout_length):
    if len(new_word) < 1:
        return "Sorry, I can't ban the empty string. Please try a message of the form '!vtban [wordToBan]'"

    banned_words[0]['banned_word'] = new_word
    banned_words[0]['infracted_at'] = current_time
    banned_words[0]['calledout_at'] = current_time - datetime.timedelta(seconds=timeout_length)
    server_dao.update_banned_word(banned_words[0])
    msg_to_send = "Ok {}, '{}' is now considered a forbidden word.".format(msg_author.mention, new_word)
    return msg_to_send

def handle_vtdelay(server_dao, current_server, time_string):
    parsed_time = parse_time(time_string)

    if parsed_time >= 0:
        current_server['timeout_duration_seconds'] = parsed_time
        server_dao.insert_server(current_server)
        formatted_time = format_seconds(parsed_time)
        return "Cool, from now on I'll wait at least {} between alerts.".format(formatted_time)
    else:
        return "Sorry, I don't understand that formatting. I was expecting something like '!vtct hh:mm:ss'"

def handle_vtct(current_time, current_server, banned_words):
    timeout_length = format_seconds(current_server['timeout_duration_seconds'])
    msg_to_send = "The cooldown period is {}.".format(timeout_length)

    for banned_word in banned_words:
        timeoutRemaining = format_time(banned_word['calledout_at'] + datetime.timedelta(seconds=current_server['timeout_duration_seconds']), current_time)
        isCooldownActive = (current_time - banned_word['calledout_at']).total_seconds() < current_server['timeout_duration_seconds']
        if isCooldownActive:
            msg_to_send += "\nI'll be able to issue another alert for '{}' in {}.".format(banned_word['banned_word'], timeoutRemaining)
        else:
            msg_to_send += "\nI'm ready to issue another warning for '{}' now.".format(banned_word['banned_word'])

    return msg_to_send

def handle_vthelp():
    msg_to_send = "You can ask me how long we've made it with '!vt'.\n"
    msg_to_send += "You can learn how long it's been since my last warning with '!vtlast'.\n"
    msg_to_send += "You can learn how long my timeout is set for, and when I can issue another warning with '!vtct'.\n"
    msg_to_send += "If you're an admin, you can silence me with '!vtsilence' or wake me back up with '!vtalert'.\n"
    msg_to_send += "If you're an admin, you can use '!vtdelay hh:mm:ss` to set the length of the timeout.\n"
    msg_to_send += "If you're an admin, you can use '!vtban word_to_ban' to change the banned word for the server.\n"
    return msg_to_send

def handle_vtlast(current_time, banned_words):
    time_without_warning = format_time(current_time, banned_words[0]['calledout_at'])
    msg_to_send = "The server last received a warning for '{}' {} ago.".format(banned_words[0]['banned_word'], time_without_warning)

    for banned_word in banned_words[1:]:
        time_without_warning = format_time(current_time, banned_word['calledout_at'])
        msg_to_send += "\nThe server last received a warning for '{}' {} ago.".format(banned_word['banned_word'], time_without_warning)

    return msg_to_send

def handle_vt(current_time, banned_words):
    timeLasted = format_time(current_time, banned_words[0]['infracted_at'])
    msg_to_send = "The server has gone {} without mentioning '{}'.".format(timeLasted, banned_words[0]['banned_word'])
    for banned_word in banned_words[1:]:
        timeLasted = format_time(current_time, banned_word['infracted_at'])
        msg_to_send += "\nThe server has gone {} without mentioning '{}'.".format(timeLasted, banned_word['banned_word'])

    msg_to_send += "\nAs a new feature, server administrators are able to change the banned word using !vtban."
    return msg_to_send

def handle_command(found_command, server_dao, current_time, current_server, banned_words, message):
    msg_to_send = ""
    if found_command is Commands.VTSILENCE:
        msg_to_send = handle_vtsilence(server_dao, current_server, message.author)
    elif found_command is Commands.VTALERT:
        msg_to_send = handle_vtalert(server_dao, current_server, message.author)
    elif found_command is Commands.VTDELAY:
        msg_to_send = handle_vtdelay(server_dao, current_server, message.content[8:])
    elif found_command is Commands.VTBAN:
        new_word = message.content[6:].lstrip().split(' ')[0]
        msg_to_send = handle_vtban(server_dao, current_time, banned_words, new_word, message.author, current_server['timeout_duration_seconds'])
    elif found_command is Commands.VTCT:
        msg_to_send = handle_vtct(current_time, current_server, banned_words)
    elif found_command is Commands.VTHELP:
        msg_to_send = handle_vthelp()
    elif found_command is Commands.VTLAST:
        msg_to_send = handle_vtlast(current_time, banned_words)
    elif found_command is Commands.VT:
        msg_to_send = handle_vt(current_time, banned_words)

    return msg_to_send

def detect_banned_word(message, banned_word):
    pattern = confusable_regex(banned_word, True)
    if re.search(pattern, message) is not None:
        return True
    return False

def handle_detected_banned_word(server_dao, current_time, current_server, message, banned_word):
    time_lasted = format_time(current_time, banned_word['infracted_at'])
    timeout_length = format_seconds(current_server['timeout_duration_seconds'])
    is_cooldown_active = (current_time - banned_word['calledout_at']).total_seconds() < current_server['timeout_duration_seconds']
    tDiff = current_time - banned_word['infracted_at']
    banned_word['infracted_at'] = current_time

    msg_to_send = ""
    if (current_server['awake'] and not is_cooldown_active):
        banned_word['calledout_at'] = current_time
        msg_to_send = "{} referenced a forbidden word, setting its counter back to 0.\n".format(message.author.mention)
        msg_to_send += "I'll wait {} before warning you for this word again.\n".format(timeout_length)
        msg_to_send += "The server went {} without mentioning the forbidden word '{}'.".format(time_lasted, banned_word['banned_word'])

    server_dao.update_banned_word(banned_word)
    print("{}::: {} lasted {} seconds.".format(current_time, current_server['server_id'], (tDiff).total_seconds()))
    return msg_to_send



def handle_message(server_dao, message, botID, current_time):
    if not message.server or message.author.bot:
        return ""

    server_id = message.server.id
    current_server = server_dao.get_server(server_id)
    if current_server is None:
        current_server = {}
        current_server['server_id'] = server_id
        bot = None
        for x in message.server.members:
            if botID == x.id:
                bot = x
                break

        fromUTC = datetime.datetime.now() - datetime.datetime.utcnow()
        current_server['awake'] = True
        current_server['timeout_duration_seconds'] = 1800
        server_dao.insert_server(current_server)
        server_dao.insert_default_banned_word(server_id, bot.joined_at + fromUTC)

    banned_words = server_dao.get_banned_words_for_server(server_id)

    found_command = parse_for_command(message.content, message.author)
    msg_to_send = handle_command(found_command, server_dao, current_time, current_server, banned_words, message)

    # Check if they've said the forbidden word
    banned_word_msg = ""
    if not found_command is Commands.VTBAN:
        for banned_word in banned_words:
            contains_banned_word = detect_banned_word(message.content, banned_word['banned_word'])
            if contains_banned_word:
                temp_msg = handle_detected_banned_word(server_dao, current_time, current_server, message, banned_word)
                if len(banned_word_msg):
                    banned_word_msg += "\n"
                banned_word_msg += temp_msg

    if len(msg_to_send) and len(banned_word_msg):
        msg_to_send += "\n"
    return msg_to_send + banned_word_msg

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
        msg_to_send = handle_message(server_dao, message, client.user.id, datetime.datetime.now())    
        if len(msg_to_send):
            await client.send_message(message.channel, msg_to_send)

    @client.event
    async def on_message(message):
        msg_to_send = handle_message(server_dao, message, client.user.id, datetime.datetime.now())    
        if msg_to_send:
            await client.send_message(message.channel, msg_to_send)

    client.run(client_key)
