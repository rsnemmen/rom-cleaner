#!/bin/bash

# Define the PATH to locate rom-cleaner.sh
ROM_CLEANER_PATH="/Users/nemmen/Dropbox/codes/shell/file-utilities/rom-cleaner"

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [--dry-run|--homebrew] <dir1> <dir2> ..."
  exit 1
fi

# Initialize arrays to hold directories and extra arguments
directories=()
extra_args=()

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --dry-run|--homebrew)
      extra_args+=("$arg") # Add optional arguments to an array
      ;;
    *)
      directories+=("$arg") # Treat other arguments as directories
      ;;
  esac
done

# Ensure at least one directory is provided
if [ "${#directories[@]}" -eq 0 ]; then
  echo "Error: No directories provided."
  exit 1
fi

# Process each directory
for dir in "${directories[@]}"; do
  if [ -d "$dir" ]; then
    # Call rom-cleaner.sh with optional arguments and print the output
    echo "Processing directory: \"$dir\""
    "$ROM_CLEANER_PATH/rom-cleaner.sh" "${extra_args[@]}" "$dir" 
  else
    echo "Error: '$dir' is not a valid directory. Skipping..."
  fi
done