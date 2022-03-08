import json
import requests
import subprocess
import os

print('Hitting discord\'s API to determine how many shards are needed.')
url = 'https://discordapp.com/api/v9/gateway/bot'
response = requests.get(url, headers = {'Authorization': 'Bot ' + os.environ["CLIENT_KEY"]})

processes = []
if (response.ok):
	jData = json.loads(response.content)
	shard_count = int(jData['shards'])
	for x in range(0, shard_count):
		processes.append(subprocess.Popen('./botLaunch.sh '+str(x)+' ' + str(shard_count), shell=True))
	print("Launched processes")
else:
	print("Can't reach the Gateway endpoint. Giving up.")

exit_codes = [p.wait() for p in processes]