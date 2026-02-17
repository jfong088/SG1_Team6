#!/bin/bash

# Ensures that the script will exit immediately if any command fails.
set -e

# Fix Volume Permissions
sudo chown -R $(whoami): /commandhistory

git clone -b 2026 --single-branch https://github.com/gcastillo56/com139-class.git 2026-2
