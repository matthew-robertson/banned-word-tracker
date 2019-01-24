import config
import bot
import sqlite3
import sys

# initialize db connection
conn = sqlite3.connect(config.DB_LOCATION)

bot.run_bot(conn, int(sys.argv[1]), int(sys.argv[2]), config.CLIENT_KEY)
