#!/usr/bin/env python3
'''
rom-cleaner: A script to filter ROM files based on a list of game names.

This script scans a directory for ROM files and cross-references their names with a 
list of desired game names provided in a text file (let's say, `keep.txt`). 
It retains only the ROMs that match the names in `keep.txt`, using case-insensitive 
substring matching. Matching files are moved to a `kept_files` subdirectory, unless 
the `--dry-run` flag is specified.

USAGE:
    keep-top.py <directory> <keep_file> [--dry-run]

ARGUMENTS:
    directory   The directory containing the ROM files to filter.
    keep_file   The path to the `keep.txt` file containing the list of games to keep.

OPTIONS:
    --dry-run   Simulates the behavior of the script without making any changes to 
                the filesystem. Prints a list of files that would be moved.

BEHAVIOR:
    - The script performs case-insensitive matching and checks if any game name in 
      `keep.txt` is a substring of the ROM filenames in the specified directory.
    - If a match is found:
        - In normal mode, the file is moved to a `kept_files` subdirectory within 
          the same directory.
        - In `--dry-run` mode, the matching files are listed but not moved.
    - Files that do not match any name in `keep.txt` are left untouched in their 
      original location.

EXAMPLES:
    1. To filter ROMs and move matching files to a subdirectory:
        python rom-cleaner.py ./roms ./keep.txt

    2. To preview which files would be kept without making changes:
        python rom-cleaner.py ./roms ./keep.txt --dry-run

NOTES:
    - The `keep.txt` file should contain one game name per line (case-insensitive).
    - Matching is performed using substring checks, so partial matches are allowed.
    - The script creates a `kept_files` subdirectory in the specified directory 
      to store the matching files.
'''


import os
import argparse
import shutil

def clean_roms(directory, keep_file, dry_run):
    # Read the list of games to keep
    with open(keep_file, 'r', encoding='utf-8') as f:
        keep_games = [line.strip().lower() for line in f.readlines()]

    # Create a list of all files in the directory
    files_in_directory = os.listdir(directory)

    if not dry_run:
        # Create a subdirectory to store the files that are kept
        keep_directory = os.path.join(directory, "kept_files")
        os.makedirs(keep_directory, exist_ok=True)
    else:
        keep_directory = None  # Not needed for dry run

    # Track files that would be moved (for dry-run output)
    kept_files = []

    # Iterate through the files in the directory
    for filename in files_in_directory:
        file_path = os.path.join(directory, filename)

        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue

        # Check if any game in keep_games is a substring of the filename
        if any(game in filename.lower() for game in keep_games):
            kept_files.append(filename)
            if not dry_run:
                # Move the file to the "kept_files" directory
                shutil.move(file_path, os.path.join(keep_directory, filename))

    # Output results
    if dry_run:
        print("Dry run: The following files would be kept:")
        for file in kept_files:
            print(f"  {file}")
    else:
        print(f"Files have been filtered. Kept files are stored in '{keep_directory}'.")

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Filter ROM files based on a list of game names in keep.txt."
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

    args = parser.parse_args()

    # Call the clean_roms function with parsed arguments
    clean_roms(args.directory, args.keep_file, args.dry_run)

if __name__ == "__main__":
    main()