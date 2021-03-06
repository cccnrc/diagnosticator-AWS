#!/bin/sh
# this script is used to boot a Docker container
source venv/bin/activate
sleep 30
while true; do
    flask db init
    flask db migrate
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
exec gunicorn -b :5000 --access-logfile - --error-logfile - main:app
