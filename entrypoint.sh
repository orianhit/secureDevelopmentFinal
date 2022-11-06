#!/bin/bash

python /app/source/manage.py migrate

# This will exec the CMD from your Dockerfile
exec "$@"
