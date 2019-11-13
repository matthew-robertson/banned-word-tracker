import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import config
import bot

def initialize_session():
    session = requests.Session()
    session.headers.update({'Authorization': 'Bot ' + config.CLIENT_KEY})
    retry = Retry(
        total=5,
        read=1,
        connect=5,
        backoff_factor=0.3,
        status_forcelist=[500],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

bot.run_bot(int(sys.argv[1]), int(sys.argv[2]), config.CLIENT_KEY, initialize_session())
