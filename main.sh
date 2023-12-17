#!/bin/bash
set -e

/usr/local/bin/python /app/main.py

if [ -f /app/post.sh ]; then
    echo Running post.sh
    chmod +x /app/post.sh
    /app/post.sh
    echo Ran post.sh
else
    echo No post.sh found
fi
