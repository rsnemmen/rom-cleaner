#!/bin/bash
#
# ROM cleaner
# =============
# Keeps only good ROM dumps and discards modifications, bad dumps, hacks, betas.
# Files retained:
#   [!]  — verified good dump
#   [U] / [u]  — US release
#   [J] / [j]  — Japan release
#   no region/dump tag at all
#
GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

usage() {
    echo "Usage: $0 [--dry-run] [--homebrew] <path_to_roms_dir>"
    exit 1
}

if [[ $# -lt 1 || $# -gt 3 ]]; then
    usage
fi

dry_run=false
homebrew=false

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

if [[ -z "$roms_dir" || ! -d "$roms_dir" ]]; then
    echo "Error: Directory '$roms_dir' does not exist."
    usage
fi

cd "$roms_dir" || exit 1

# Allow empty dirs without iterating over a literal '*'
shopt -s nullglob

for rom in *; do
    # Skip subdirectories
    [[ -f "$rom" ]] || continue

    keep=false

    # Hacks and betas are never kept, regardless of other tags
    if [[ "$rom" =~ [Hh]ack ]]; then
        echo -e "${RED}Deleting:${RESET} $rom"
        [[ "$dry_run" == false ]] && rm "$rom"
        continue
    fi

    if [[ "$rom" =~ \([Bb]eta\) ]]; then
        echo -e "${RED}Deleting:${RESET} $rom"
        [[ "$dry_run" == false ]] && rm "$rom"
        continue
    fi

    # Homebrew ("Game by Author") — optional
    if [[ "$homebrew" == true && "$rom" =~ " by " ]]; then
        echo -e "${RED}Deleting:${RESET} $rom"
        [[ "$dry_run" == false ]] && rm "$rom"
        continue
    fi

    # Keep verified good dumps
    if [[ "$rom" =~ \[!\] ]]; then
        keep=true
    fi

    # Keep US releases (case-insensitive)
    if [[ "$rom" =~ \[[Uu]\] ]]; then
        keep=true
    fi

    # Keep Japan releases (case-insensitive)
    if [[ "$rom" =~ \[[Jj]\] ]]; then
        keep=true
    fi

    # Keep ROMs with no bracketed tags and not a beta
    if ! [[ "$rom" =~ \[[^\]]*\] ]] && ! [[ "$rom" =~ \([Bb]eta\) ]]; then
        keep=true
    fi

    if [[ "$keep" == true ]]; then
        echo -e "${GREEN}Keeping:${RESET} $rom"
    else
        echo -e "${RED}Deleting:${RESET} $rom"
        [[ "$dry_run" == false ]] && rm "$rom"
    fi
done
