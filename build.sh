#!/bin/bash

# Build the project
echo "Building the project..."
py -m pip install -r requirements.txt

echo "Make Migrations..."
py manage.py makemigrations --noinput
py manage.py migrate --noinput

echo "Collect Static..."
py manage.py collectstatic --noinput --clear