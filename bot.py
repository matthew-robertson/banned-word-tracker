from collections import defaultdict
import datetime
import discord
import json
import os

from serverobjects.server import DiscordServer
from utils.time import parse_time, format_time, format_seconds
from commands import TimerCommand, CooldownCommand, HelpCommand, SilenceCommand, AlertCommand, AddBanCommand, RemoveBanCommand, ChangeBanCommand, ChangeTimeCommand, NoCommand

API_BASE_URL = os.environ["API_BASE_URL"]

command_map = defaultdict(
    lambda: NoCommand,
    {
        '!vtsilence': SilenceCommand,
        '!vtalert': AlertCommand,
        '!vtdelay': ChangeTimeCommand,
        '!vtban': AddBanCommand,
        '!vtswapban': ChangeBanCommand,
        '!vtunban': RemoveBanCommand,
        '!vthelp': HelpCommand,
        '!vtct': CooldownCommand,
        '!vt': TimerCommand
    })

callout_phrase = (
    "{} referenced a forbidden word, setting its counter back to 0.\n"
    "I'll wait {} before warning you for this word again.\n"
    "The server went {} without mentioning the forbidden word '{}'.")

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
    timeout_length = format_seconds(current_server.timeout_duration_seconds)
    banned_word.send_infringing_message(current_time, called_out)
    
    if not called_out:
        return ""
    return callout_phrase.format(author.mention, timeout_length, time_lasted, banned_word.banned_word)

def get_infringing_bans(banned_words, message, check_words):
    if not check_words:
        return []
    return filter(
        lambda ban: ban.check_if_message_infringes(message),
        banned_words)

def handle_message(message, current_time, session):
    if not message.guild or message.author.bot:
        return ""

    server_id = message.guild.id
    current_server = fetch_server_from_api(server_id, current_time, session)

    permissions = None
    if (hasattr(message.author, 'permissions_in')):
        permissions = message.author.permissions_in(message.channel)

    found_command = command_map[message.content.split(' ')[0]]()
    if (not found_command.is_command_authorized(permissions)):
        msg_to_send = "Sorry, you don't have permissions for this."
    else:
        msg_to_send = found_command.execute(current_server, current_time, message.content, message.author)

    infringing_words = get_infringing_bans(current_server.banned_words, message.content, found_command.detect_bans_in_message)
    banned_word_msg = "\n".join(map(
        lambda ban: handle_detected_banned_word(current_time, current_server, message.author, ban),
        infringing_words))

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
