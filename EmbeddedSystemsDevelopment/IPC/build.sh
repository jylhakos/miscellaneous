#!/bin/bash

# Qt D-Bus IPC Example Build Script
# This script builds both server and client components

set -e  # Exit on any error

echo "=== Qt D-Bus IPC Example Build Script ==="
echo "Building server and client components..."
echo

# Check if Qt is available
if ! command -v qmake &> /dev/null; then
    echo "Error: qmake not found. Please install Qt development packages:"
    echo "  Ubuntu/Debian: sudo apt-get install qt6-base-dev qt6-tools-dev libqt6dbus6-dev"
    echo "  Or download Qt from: https://www.qt.io/download"
    exit 1
fi

# Check if D-Bus development files are available
if ! pkg-config --exists dbus-1; then
    echo "Warning: D-Bus development files not found."
    echo "Install with: sudo apt-get install libdbus-1-dev"
fi

# Build server
echo "Building server..."
cd src/server
qmake server.pro
make clean
make
if [ $? -eq 0 ]; then
    echo "✅ Server built successfully: qt_ipc_server"
else
    echo "❌ Server build failed"
    exit 1
fi
cd ../..

# Build client  
echo "Building client..."
cd src/client
qmake client.pro
make clean
make
if [ $? -eq 0 ]; then
    echo "✅ Client built successfully: qt_ipc_client"
else
    echo "❌ Client build failed"
    exit 1
fi
cd ../..

echo
echo "=== Build completed successfully! ==="
echo
echo "To run the example:"
echo "1. Start the server: ./src/server/qt_ipc_server"
echo "2. In another terminal, run client: ./src/client/qt_ipc_client"
echo
echo "For debugging D-Bus traffic:"
echo "  dbus-monitor --session"
echo
echo "To check if D-Bus session is running:"
echo "  pgrep -f dbus-daemon"
echo "  Or start with: eval \`dbus-launch --sh-syntax\`"
