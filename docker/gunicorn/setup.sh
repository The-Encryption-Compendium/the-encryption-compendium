#!/bin/sh

###
### Install dependencies for the container image
###

# Exit if any command fails
set -e

# Install build tools
apk add --no-cache gcc

# Install Python dependencies using Pip
python3 -m pip install \
    --no-cache-dir \
    -r /tmp/requirements.txt

if [ "${DEVELOPMENT}" = "yes" ]
then
    python3 -m pip install \
        --no-cache-dir \
        -r /tmp/requirements.dev.txt
fi

# Clean up (remove unneeded files and dependencies)
apk del gcc
rm /tmp/requirements*.txt
rm "$0"
