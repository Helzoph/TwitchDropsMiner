#!/usr/bin/env bash

dirpath=$(dirname "$(readlink -f "$0")")

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo
    echo "No git executable found in PATH!"
    echo
    read -p "Press any key to continue..."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo
    echo "No uv executable found in PATH!"
    echo "Please install uv: https://github.com/astral-sh/uv"
    echo
    read -p "Press any key to continue..."
    exit 1
fi

# Sync dependencies using uv
echo
echo "Syncing dependencies with uv..."
uv sync
if [ $? -ne 0 ]; then
    echo
    echo "Failed to sync dependencies."
    echo
    read -p "Press any key to continue..."
    exit 1
fi

echo
echo "Environment setup completed successfully using uv."
echo
read -p "Press any key to continue..."
