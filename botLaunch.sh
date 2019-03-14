#!/bin/bash

until python 'main.py' $1 $2; do
    echo "Bot instance " $1 " crashed.  Respawning.." >&2
    sleep 1
done