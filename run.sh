#!/bin/bash

# Create a script that loads environment for the cron job
printenv | sed 's/^\([a-zA-Z0-9_]*\)=\(.*\)$/export \1="\2"/g' > /app/env.sh
chmod +x /app/env.sh

# Add a cron job to run main.py every 5 minutes
echo "*/5 * * * * . /app/env.sh; /app/main.sh >> /var/log/cron.log 2>&1" | crontab -

# Create the log file to be able to run tail
touch /var/log/cron.log

/app/main.sh && cron && tail -f /var/log/cron.log
