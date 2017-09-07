import discord
import asyncio
import re
import datetime
import math

# A pattern to match the word vore, and only the single word vore.
pattern = re.compile(r'\b[V|v][O|o][R|r][E|e]\b')
serverAndDate = {}
botStartup = datetime.datetime.now()

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    global botStartup
    currentTime = datetime.datetime.now()
    lastReferenced = client.user.joined_at
    if message.server in serverAndDate:
        lastReferenced = serverAndDate[message.server]

    diff = currentTime - lastReferenced
    hours = math.floor(diff.seconds/3600)
    seconds = diff.seconds - hours * 3600

    if message.content.startswith('!vt'):
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        await client.edit_message(tmp, 'The server has gone {} days, {} hours, and {} seconds without mentioning vore (aside from these messages).'.format(diff.days, hours, seconds))
    elif pattern.search(message.content) is not None and message.author.id is not client.user.id:
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        serverAndDate[message.server] = currentTime
        await client.edit_message(tmp, '{} referenced vore, setting the counter back to 0.\n The server went {} days, {} hours, and {} seconds without mentioning vore.'.format(message.author.mention, diff.days, hours, seconds))

client.run('MzU1MTQ0NDUwNDM3MDIxNjk3.DJIlnQ.Yg56nQ6JdLbxUDmlkFnuu6ay2FM')