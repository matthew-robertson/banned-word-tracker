import json
import requests
import subprocess
import config

print('Hitting discord\'s API to determine how many shards are needed.')
key = config.CLIENT_KEY

url = 'https://discordapp.com/api/v6/gateway/bot?token=' + key
response = requests.get(url)

processes = []
if (response.ok):
	jData = json.loads(response.content)
	shard_count = int(jData['shards'])
	for x in range(0, shard_count):
		processes.append(subprocess.Popen(['python', 'main.py', str(x), str(shard_count)]))
	print("Launched processes")
	with open("logs/pids.txt", "w") as target:
		for process in processes:
			target.write('{}\n'.format(process.pid))
else:
	print("Can't reach the Gateway endpoint. Giving up.")