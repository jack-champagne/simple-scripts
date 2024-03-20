#!/usr/bin/env bash

BACKUP_PATH="/mnt/full-backup"
# Use an array to hold each exclude pattern
EXCLUDE_DIRS=( "/dev/*" "/proc/*" "/sys/*" "/tmp/*" "/run/*" "/mnt/*" "/media/*" "/lost+found" "/home/jack/Documents/Drive" "/home/jack/Documents/OneDrive-CMU" "Drive-Shared" )
SOURCE_DIR="/"

# Build the exclude parameters by iterating over the array
EXCLUDE_PARAMS=""
for dir in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_PARAMS+="--exclude=${dir} "
done

# Use the built exclude parameters in the rsync command
# Note: It's important to use unquoted variable expansion to allow word splitting for each exclude parameter
echo "sudo rsync -aAXv ${SOURCE_DIR} ${EXCLUDE_PARAMS} ${BACKUP_PATH}"

# Execute the rsync command and capture its exit status
sudo rsync -aAXv ${SOURCE_DIR} ${EXCLUDE_PARAMS} ${BACKUP_PATH}

if [ $? -eq 0 ]; then
    echo "Backup completed successfully"
else
    echo "Some error occurred during backup"
fi
