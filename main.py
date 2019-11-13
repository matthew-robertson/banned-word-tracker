import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import config
import bot

def initialize_session():
    session = requests.Session()
    session.headers.update({'Authorization': 'Bot ' + config.CLIENT_KEY})
    #retry = Retry(
    #    total=retries,
    #    read=retries,
    #    connect=retries,
    #    backoff_factor=backoff_factor,
    #    status_forcelist=status_forcelist,
    #)
    #adapter = HTTPAdapter(max_retries=retry)
    #session.mount('http://', adapter)
    #session.mount('https://', adapter)
    return session

bot.run_bot(int(sys.argv[1]), int(sys.argv[2]), config.CLIENT_KEY, initialize_session())
