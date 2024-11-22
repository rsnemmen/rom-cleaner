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

def load_keep_list(file_path):
    """
    Load the list of games to keep from the specified text file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit(1)

def matches_keep_list(filename, keep_list):
    """
    Check if the file matches any entry in the keep list.
    Matching is case-insensitive and based on substring containment.
    """
    for game in keep_list:
        if game.lower() in filename.lower():
            return True
    return False

def confirm_action():
    """
    Prompt the user for confirmation before proceeding with deletion.
    """
    while True:
        response = input("Are you sure you want to delete the unmatched files? (Y/n): ").strip().lower()
        if response in {"y", "yes", ""}:
            return True
        elif response in {"n", "no"}:
            return False
        else:
            print("Please enter 'Y' or 'n'.")

def main():
    parser = argparse.ArgumentParser(description="Filter ROM files based on a keep list.")
    parser.add_argument("directory", type=str, help="The directory containing the ROM files.")
    parser.add_argument("keep_file", type=str, help="The text file listing games to keep.")
    parser.add_argument("--dry-run", action="store_true", help="Do not delete files, only show what would be kept.")
    
    args = parser.parse_args()
    
    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"Error: The directory '{args.directory}' does not exist.")
        exit(1)
    
    # Load the keep list
    keep_list = load_keep_list(args.keep_file)
    if not keep_list:
        print("Error: The keep list is empty.")
        exit(1)

    # List all files in the directory (skip subdirectories)
    files_in_directory = [
        f for f in os.listdir(args.directory) 
        if os.path.isfile(os.path.join(args.directory, f))
    ]
    files_to_keep = []
    files_to_delete = []

    # Determine which files to keep and delete
    for filename in files_in_directory:
        if matches_keep_list(filename, keep_list):
            files_to_keep.append(filename)
        else:
            files_to_delete.append(filename)

    # Display results
    if files_to_keep:
        print("The following files will be kept:")
        for file in files_to_keep:
            print(f"  {file}")
    else:
        print("No files match the keep list. All files will be deleted.")

    # Dry-run or actual deletion
    if args.dry_run:
        print("\nDry run mode: No files were deleted.")
    else:
        if files_to_delete:
            # Confirm action
            if confirm_action():
                delete_count = 0
                for file in files_to_delete:
                    file_path = os.path.join(args.directory, file)
                    os.remove(file_path)
                    delete_count += 1
                print(f"\n{delete_count} unmatched file{'s' if delete_count > 1 else ''} have been deleted.")
            else:
                print("\nOperation cancelled.")
        else:
            print("\nNo files to delete. All files match the keep list.")

if __name__ == "__main__":
    main()