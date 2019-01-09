import sqlite3
from sqlite3 import Error

# When a configuration file becomes a thing, the db location should 100% go there
try:
  conn = sqlite3.connect('/home/njwoodge/Documents/tracker.db')
except Error as e:
  print(e)
