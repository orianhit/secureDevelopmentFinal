#!/bin/bash

while !  wget db:3306; do 
	echo 'w8ing for db'
	sleep 1 
done

python /app/source/manage.py migrate

# This will exec the CMD from your Dockerfile
exec "$@"
