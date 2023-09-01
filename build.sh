#!/bin/bash

# Build the project
echo "Building the project..."
python3.11.4 -m pip install -r requirements.txt

echo "Make Migrations..."
python3.11.4 manage.py makemigrations --noinput
python3.11.4 manage.py migrate --noinput

echo "Collect Static..."
Python3.11.4 manage.py collectstatic --noinput --clear