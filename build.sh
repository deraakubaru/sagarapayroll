#!/bin/bash

# Build the project

python -m venv venv
.\venv\Scripts\activate

echo "Building the project..."
pip install -r requirements.txt

echo "Make Migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collect Static..."
python manage.py collectstatic --noinput --clear