#!/bin/bash

# Resolve rom-cleaner.sh relative to this script's own directory
ROM_CLEANER_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [--dry-run] [--homebrew] [--convention <name>] <dir1> <dir2> ..."
  exit 1
fi

# Initialize arrays to hold directories and extra arguments
directories=()
extra_args=()

# Parse arguments
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run|--homebrew)
      extra_args+=("$1")
      shift
      ;;
    --convention)
      if [ "$#" -lt 2 ]; then
        echo "Error: --convention requires a value."
        exit 1
      fi
      extra_args+=("$1" "$2")
      shift 2
      ;;
    --convention=*)
      extra_args+=("$1")
      shift
      ;;
    *)
      directories+=("$1")
      shift
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
