from collections import defaultdict
import datetime
import discord
import json
import os

from serverobjects.server import DiscordServer
from utils.time import parse_time, format_time, format_seconds
from commands import TimerCommand, CooldownCommand, HelpCommand, SilenceCommand, AlertCommand, AddBanCommand, RemoveBanCommand, RemoveBanWordCommand, ChangeBanCommand, ChangeTimeCommand, ChangePrefixCommand, ListRecordCommand, NoCommand

API_BASE_URL = os.environ["API_BASE_URL"]

command_map = defaultdict(
    lambda: NoCommand,
    {
        'silence': SilenceCommand,
        'alert': AlertCommand,
        'delay': ChangeTimeCommand,
        'prefix': ChangePrefixCommand,
        'ban': AddBanCommand,
        'swapban': ChangeBanCommand,
        'unban': RemoveBanCommand,
        'unbanw': RemoveBanWordCommand,
        'help': HelpCommand,
        'ct': CooldownCommand,
        'r': ListRecordCommand,
        '': TimerCommand
    })

callout_phrase = "{} referenced the forbidden word '{}', breaking a streak of {}."

def fetch_server_from_api(server_id, current_time, session):
    response = session.get(API_BASE_URL + 'v1/servers/' + str(server_id))
    if (not response.ok):
        response = session.post(
            API_BASE_URL + 'v1/servers', 
            json = {'server_id': server_id})
    
    if (response.ok):
        jData = json.loads(response.content)
        return DiscordServer(jData, current_time, session)

def handle_detected_banned_word(current_time, current_server, author, banned_word):
    called_out = current_server.awake and not banned_word.is_cooldown_active
    time_lasted = format_time(current_time, banned_word.infracted_at)
    banned_word.send_infringing_message(current_time, author, called_out)
    
    if not called_out:
        return ""
    return callout_phrase.format(author.mention, banned_word.banned_word, time_lasted)

def get_infringing_bans(banned_words, message, check_words):
    if not check_words:
        return []
    return [ban for ban in banned_words if ban.check_if_message_infringes(message)]

def handle_message(message, current_time, session):
    if not message.guild or message.author.bot:
        return ""

    server_id = message.guild.id
    current_server = fetch_server_from_api(server_id, current_time, session)

    permissions = None
    if (hasattr(message.author, 'permissions_in')):
        permissions = message.author.permissions_in(message.channel)

    found_command = NoCommand()
    first_word = message.content.split(' ')[0]
    if first_word.startswith(current_server.prefix):
        found_command = command_map[first_word[len(current_server.prefix):]]()
    if first_word.startswith('!vthelp'):
        found_command = HelpCommand()

    if (not found_command.is_command_authorized(permissions)):
        msg_to_send = "Sorry, you don't have permissions for this."
    else:
        msg_to_send = found_command.execute(current_server, current_time, message.content, message.author)

    infringing_words = get_infringing_bans(current_server.banned_words, message.content, found_command.detect_bans_in_message)
    banned_word_msgs = [handle_detected_banned_word(current_time, current_server, message.author, ban) for ban in infringing_words]
    banned_word_msgs = [msg for msg in banned_word_msgs if len(msg)]
    banned_word_msg = "\n".join(banned_word_msgs)
    if len(banned_word_msgs) > 0:
        timeout_length = format_seconds(current_server.timeout_duration_seconds)
        banned_word_msg += "\nI'll wait {} before warning you for ".format(timeout_length)
        if len(banned_word_msgs) > 2:
            banned_word_msg += "one of these words again."
        else:
            banned_word_msg += "this word again."
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
        if msg_to_send:
            await message.channel.send(msg_to_send)

    @client.event
    async def on_message(message):
        msg_to_send = handle_message(message, datetime.datetime.now(), session)    
        if msg_to_send:
            await message.channel.send(msg_to_send)

    client.run(client_key)
