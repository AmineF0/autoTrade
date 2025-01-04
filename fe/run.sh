#!/bin/sh

# Check if the BACK_END_SERVER_URL environment variable is set
if [ -z ${BACK_END_SERVER_URL+x} ]; then
  echo "Error: BACK_END_SERVER_URL environment variable is not set."
  exit 1
fi

# Directory to search for files
DIRECTORY="./build"

# Replace occurrences of 'http://localhost:5000' with the value of BACK_END_SERVER_URL in all files within the specified directory
find "$DIRECTORY" -type f -exec sed -i "s|http://127.0.0.1:8000|$BACK_END_SERVER_URL|g" {} +

echo "Replacement complete."

# Start the nginx server
serve -s build
