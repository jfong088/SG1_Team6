#!/bin/bash

# Ensures that the script will exit immediately if any command fails.
set -e

# Fix Volume Permissions
sudo chown -R $(whoami): /commandhistory

