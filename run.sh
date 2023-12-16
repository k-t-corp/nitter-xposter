#!/bin/bash

# Create a script that loads environment for the cron job
printenv | sed 's/^\([a-zA-Z0-9_]*\)=\(.*\)$/export \1="\2"/g' > /app/env.sh
chmod +x /app/env.sh

# Add a cron job to run main.py every 5 minutes
crontab -l; echo "*/5 * * * * . /app/env.sh; printev; /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1" | crontab -

# Create the log file to be able to run tail
touch /var/log/cron.log

/usr/local/bin/python main.py && cron && tail -f /var/log/cron.log
