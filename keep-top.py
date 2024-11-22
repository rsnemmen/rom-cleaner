#!/usr/bin/env python3
'''
keep-top: A script to filter ROM files based on a list of game names.

This script scans a directory for ROM files and cross-references their names with a 
list of desired game names provided in a text file (let's say, `keep.txt`). 
It retains only the ROMs that match the names in `keep.txt`, using case-insensitive 
substring matching. Matching files are moved to a `kept_files` subdirectory, unless 
the `--dry-run` flag is specified.

USAGE:
    keep-top.py <dir> <keep_file> [--dry-run]

ARGUMENTS:
    dir   The directory containing the ROM files to filter.
    keep_file   The path to the `keep.txt` file containing the list of games to keep.

OPTIONS:
    --dry-run   Simulates the behavior of the script without making any changes to 
                the filesystem. Prints a list of files that would be moved.

BEHAVIOR:
    - The script performs case-insensitive matching and checks if any game name in 
      `keep.txt` is a substring of the ROM filenames in the specified directory.
    - If a match is found:
        - In normal mode, all files not matching are removed, so be careful!
        - In `--dry-run` mode, the matching files are listed but not moved.

EXAMPLES:
    1. To filter ROMs and remove non-matching games:
        keep-top.py ./roms ./keep.txt

    2. To preview which files would be kept without making changes:
        keep-top.py ./roms ./keep.txt --dry-run
'''

import os
import argparse

def clean_roms(directory, keep_file, dry_run, extensions):
    """
    Print the files that will be kept based on the keep_file, and optionally delete non-matching files.

    Args:
        directory (str): The directory containing the ROM files.
        keep_file (str): Path to the keep.txt file containing the list of game names to keep.
        dry_run (bool): If True, simulate the behavior without modifying the filesystem.
        extensions (list): List of file extensions to process (e.g., ['.sms']).

    Behavior:
        - Reads game names from the keep.txt file.
        - Prints the files that match any name in keep.txt and have one of the allowed extensions.
        - Optionally deletes all other files if dry_run is not set.
        - Skips the keep.txt file itself.
        - Case-insensitive substring matching is used to determine matches.
    """
    # Read the list of games to keep
    with open(keep_file, 'r', encoding='utf-8') as f:
        keep_games = [line.strip().lower() for line in f.readlines()]

    # List all files in the directory
    files_in_directory = os.listdir(directory)

    # Track files that will be kept
    kept_files = []

    # Iterate through the files in the directory
    for filename in files_in_directory:
        file_path = os.path.join(directory, filename)

        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue

        # Skip the keep.txt file itself
        if os.path.abspath(file_path) == os.path.abspath(keep_file):
            continue

        # Check if the file has one of the allowed extensions
        if not any(filename.lower().endswith(ext) for ext in extensions):
            continue

        # Check if the file matches any of the game names in keep_games
        if any(game in filename.lower() for game in keep_games):
            # File matches; add to the kept list
            kept_files.append(filename)
        else:
            # File does not match; delete if not in dry-run mode
            if not dry_run:
                os.remove(file_path)

    # Output results
    print("The following files will be kept:")
    for file in kept_files:
        print(f"  {file}")

    if not dry_run:
        print(f"Deleted {len(files_in_directory) - len(kept_files)} files that did not match the keep list.")
    else:
        print("Dry run: No files were deleted.")


def main():
    """
    Entry point for the script. Parses command-line arguments and runs the script.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Filter ROM files based on a list of game names in keep.txt, deleting non-matching files."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The directory containing the ROM files."
    )
    parser.add_argument(
        "keep_file",
        type=str,
        help="The path to the keep.txt file containing game names to keep."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the script without making changes to the disk."
    )
    parser.add_argument(
        "--extensions",
        type=str,
        default=".sms",
        help="Comma-separated list of file extensions to process (default: .sms)."
    )

    args = parser.parse_args()

    # Parse the extensions argument into a list of extensions
    extensions = [ext.strip().lower() for ext in args.extensions.split(",")]

    # Call the clean_roms function with parsed arguments
    clean_roms(args.directory, args.keep_file, args.dry_run, extensions)


if __name__ == "__main__":
    main()