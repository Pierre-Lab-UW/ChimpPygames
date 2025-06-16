#!/bin/bash

# Directory to check for
TARGET_DIR="/home/pi/myproject"  # <-- Change this to your directory

# Log file for debugging (optional)
LOGFILE="/home/pi/git_autopull.log"

# Check if the directory exists
if [ -d "$TARGET_DIR" ]; then
    echo "$(date): Found directory $TARGET_DIR" >> "$LOGFILE"
    cd "$TARGET_DIR" || exit

    # Run git pull from the main branch
    git pull origin main >> "$LOGFILE" 2>&1
else
    echo "$(date): Directory $TARGET_DIR not found" >> "$LOGFILE"
fi
