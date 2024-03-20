#!/bin/env sh

# Check if number of forwards is provided as argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number of forwards>"
    exit 1
fi

# Extract the number of forwards
N=$1

# SSH command template
ssh_command="ssh -N nixbox"

# Add forwards to the SSH command
for ((i=0; i<$N; i++)); do
    ssh_command+=" -L $((8700+i)):localhost:$((8700+i))"
done

# Execute the SSH command
eval "$ssh_command"
