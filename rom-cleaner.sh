#!/bin/bash
#
# ROM cleaner
# =============
# This script will delete all modifications, bad dumps, keeping only:
#
# - [!]: Indicates a good, verified dump. You generally want to keep these versions.
# - No tag: If there's no extra tag, the ROM is likely the original version.
# - [U] for the US, [J] for Japan
#
# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

# Function to display usage information
usage() {
    echo "Usage: $0 [--dry-run] [--homebrew] <path_to_roms_dir>"
    exit 1
}

# Check if the correct number of arguments is provided
if [[ $# -lt 1 || $# -gt 3 ]]; then
    usage
fi

# Initialize variables
dry_run=false
homebrew=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            dry_run=true
            shift
            ;;
        --homebrew)
            homebrew=true
            shift
            ;;
        *)
            roms_dir="$1"
            shift
            ;;
    esac
done

# Ensure the ROMs directory is set and exists
if [[ -z "$roms_dir" || ! -d "$roms_dir" ]]; then
    echo "Error: Directory '$roms_dir' does not exist."
    usage
fi

# Change to the ROMs directory
cd "$roms_dir" || exit

# Process each ROM file in the directory
for rom in *; do
    # Initialize a flag to determine whether to keep the ROM
    keep=false

    # Condition 1: Keep if the ROM has a [!] tag
    if [[ "$rom" =~ \[!\] ]]; then
        keep=true
    fi

    # Condition 2: Keep if the ROM has a [U] tag
    if [[ "$rom" =~ \[U\] ]]; then
        keep=true
    fi

    # Condition 3: Keep if the ROM has a [J] tag
    if [[ "$rom" =~ \[J\] ]]; then
        keep=true
    fi

    # Condition 4: Keep if the ROM has no tags and is not marked as a beta or hack
    if ! [[ "$rom" =~ \[[^\]]*\] ]] && ! [[ "$rom" =~ \([Bb]eta\) ]]; then
        keep=true
    fi

    # Condition 5: Do NOT keep if the ROM has "Hack" or "hack" in the name
    if [[ "$rom" =~ [Hh]ack ]]; then
        keep=false
    fi

    # Condition 6: If --homebrew is used, do NOT keep if the ROM has " by " in the name
    if [[ "$homebrew" == true && "$rom" =~ " by " ]]; then
        keep=false
    fi

    # Decide whether to keep or delete the ROM based on the `keep` flag
    if [[ "$keep" == true ]]; then
        echo -e "${GREEN}Keeping:${RESET} $rom"
    else
        echo -e "${RED}Deleting:${RESET} $rom"
        # Only delete if not in dry-run mode
        if [[ "$dry_run" == false ]]; then
            rm "$rom"
        fi
    fi
done