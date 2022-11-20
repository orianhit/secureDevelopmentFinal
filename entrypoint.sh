#!/bin/bash

while !  wget db:3306; do 
	sleep 5
done

python /app/source/manage.py collectstatic --noinput
python /app/source/manage.py migrate

# This will exec the CMD from your Dockerfile
exec "$@"