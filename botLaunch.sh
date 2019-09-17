#!/bin/bash

while true; do
	python 'main.py' $1 $2
    echo "Bot instance " $1 " crashed.  Respawning.." >&2
    sleep 1
done