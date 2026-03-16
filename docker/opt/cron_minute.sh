#!/bin/bash

source /opt/.env.sh

cd /app

python manage.py cleartokens

python manage.py cleartasks

python manage.py send_dossier_notifications

python manage.py send_compliance_reminders 