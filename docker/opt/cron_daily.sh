#!/bin/bash

source /opt/.env.sh

cd /app

python manage.py trainingschedules

python manage.py trainingreminders
