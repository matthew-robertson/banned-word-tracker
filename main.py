import config
import bot
import sys

bot.run_bot(int(sys.argv[1]), int(sys.argv[2]), config.CLIENT_KEY)
