#!/bin/bash

# --- Configuration ---
TARGET_DIR="/home/pi/myproject"       # Change this to your repo directory
LOGFILE="/home/pi/git_autopull.log"   # Log file
PING_HOST="8.8.8.8"                   # A stable host to ping
MAX_WAIT_TIME=120                     # Max seconds to wait for network
WAIT_INTERVAL=5                       # Seconds between pings

echo "$(date): Starting git_autopull.sh" >> "$LOGFILE"

# Wait for network
elapsed=0
until ping -c 1 -W 2 "$PING_HOST" > /dev/null 2>&1; do
    echo "$(date): Waiting for network..." >> "$LOGFILE"
    sleep "$WAIT_INTERVAL"
    elapsed=$((elapsed + WAIT_INTERVAL))
    if [ "$elapsed" -ge "$MAX_WAIT_TIME" ]; then
        echo "$(date): Network not available after $MAX_WAIT_TIME seconds. Exiting." >> "$LOGFILE"
        exit 1
    fi
done

echo "$(date): Network is up!" >> "$LOGFILE"

# Check for the repo directory
if [ -d "$TARGET_DIR" ]; then
    echo "$(date): Found directory $TARGET_DIR" >> "$LOGFILE"
    cd "$TARGET_DIR" || exit
    git pull origin main >> "$LOGFILE" 2>&1
    echo "$(date): git pull complete" >> "$LOGFILE"
else
    echo "$(date): Directory $TARGET_DIR not found!" >> "$LOGFILE"
fi

#test commit comment