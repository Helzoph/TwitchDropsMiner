#!/usr/bin/env bash

dirpath=$(dirname "$(readlink -f "$0")")

# Run PyInstaller using uv run
echo
echo "Building with uv run pyinstaller..."
uv run pyinstaller "$dirpath/build.spec"
if [ $? -ne 0 ]; then
    echo
    echo "PyInstaller build failed."
    echo
    [ "$1" != "--nopause" ] && read -p "Press any key to continue..."
    exit 1
fi

echo
echo "Build completed successfully."
echo
[ "$1" != "--nopause" ] && read -p "Press any key to continue..."
