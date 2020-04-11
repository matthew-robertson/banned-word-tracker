bot:
	python startup.py

test:
	python -m unittest discover

tester:
	docker run --entrypoint /bin/bash -it --env-file testenv.conf --mount src="$(pwd)",target=/usr/src/app,type=bind bwb