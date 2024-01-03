#!/bin/bash

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define the SSH command
SSH_CMD="ssh -tt -i /config/.ssh/id_ed25519 root@xxx.xxx.xxx.xxx -p 22222 -o StrictHostKeyChecking=no"

# Define the Docker command to run esphome from the CLI
DOCKER_CMD="docker exec addon_5c53de3b_esphome esphome run --no-logs --device xxx.xxx.xxx.xxx /config/esphome/variable-message-display.yaml"

# Define the log file
LOGFILE="$DIR/pokemon_update.log"

# Combine the SSH and Docker commands
CMD="$SSH_CMD '$DOCKER_CMD'"

# Run the combined command and redirect stdout and stderr to the log file
eval $CMD > $LOGFILE 2>&1
