import discord
import asyncio
import re
import datetime
import math

# A pattern to match the word vore, and only the single word vore.
pattern = re.compile(r'\b[V|v][O|o][R|r][E|e]\b')
serverAndDate = {}
botStartup = datetime.datetime.now()
lastMention = datetime.datetime.now() - datetime.timedelta(days=1)


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
    
    bot = None
    for x in message.server.members:
        if client.user.id == x.id:
            bot = x
            break
    # Timezone hack, apparently isn't needed for Heroku.
    lastReferenced = bot.joined_at #- datetime.timedelta(hours=4)
    if message.server in serverAndDate:
        lastReferenced = serverAndDate[message.server]

    print(lastReferenced)
    print(currentTime)
    diff = currentTime - lastReferenced
    hours = math.floor(diff.seconds/3600)
    minutes = math.floor((diff.seconds - hours * 3600)/60)
    seconds = diff.seconds - hours * 3600 - minutes * 60

    if message.content.startswith('!vt'):
        await client.send_message('The server has gone {} days, {} hours, {} minutes, and {} seconds without mentioning vore (aside from these messages).'.format(diff.days, hours, minutes, seconds))
    elif pattern.search(message.content) is not None and message.author.id is not client.user.id:
        serverAndDate[message.server] = currentTime
        if ((currentTime - lastMention).seconds >= 900):
            await client.send_message('{} referenced vore, setting the counter back to 0.\n The server went {} days, {} hours, {} minutes, and {} seconds without mentioning vore.'.format(message.author.mention, diff.days, hours, minutes, seconds))
            lastMention = currentTime

client.run('MzU1MTQ0NDUwNDM3MDIxNjk3.DJIlnQ.Yg56nQ6JdLbxUDmlkFnuu6ay2FM')