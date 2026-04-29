#!/usr/bin/env python3
'''
keep-top: Filter ROM files using fuzzy name matching.

Scans a directory for ROM files and cross-references their names with a list
of desired game names from a text file (e.g. keep.txt). Files whose names
do not fuzzy-match any entry in the keep list are deleted. Matching uses
case-insensitive fuzzy scoring (rapidfuzz WRatio) after stripping region/dump
tags like (U), [!], and (USA) from filenames, so "aladdin" matches both
"Aladdin (U) [!].smc" and "Aladdin (USA) (Rev 1).zip".

USAGE:
    keep-top.py <dir> <keep_file> [--dry-run] [--threshold N]

ARGUMENTS:
    dir         Directory containing the ROM files to filter.
    keep_file   Text file listing games to keep (one name per line).

OPTIONS:
    --dry-run       Show what would be kept/deleted without making any changes.
    --threshold N   Minimum fuzzy match score 0-100 (default: 50).
'''

import os
import argparse
from fuzzycp import file_matching

from rom_naming import normalize_rom_title


def load_keep_list(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit(1)


def confirm_action():
    while True:
        response = input("Are you sure you want to delete the unmatched files? (Y/n): ").strip().lower()
        if response in {"y", "yes", ""}:
            return True
        elif response in {"n", "no"}:
            return False
        else:
            print("Please enter 'Y' or 'n'.")


def main():
    parser = argparse.ArgumentParser(description="Filter ROM files using fuzzy name matching.")
    parser.add_argument("directory", type=str, help="Directory containing the ROM files.")
    parser.add_argument("keep_file", type=str, help="Text file listing games to keep.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be kept/deleted without making any changes.")
    parser.add_argument("--threshold", type=int, default=50, metavar="N",
                        help="Minimum fuzzy match score 0-100 (default: 50).")

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: The directory '{args.directory}' does not exist.")
        exit(1)

    keep_list = load_keep_list(args.keep_file)
    if not keep_list:
        print("Error: The keep list is empty.")
        exit(1)

    files_in_directory = [
        f for f in os.listdir(args.directory)
        if os.path.isfile(os.path.join(args.directory, f))
    ]

    if not files_in_directory:
        print("No files found in directory.")
        return

    # Clean filenames for fuzzy matching using the same parser as rom-cleaner.
    files_cleaned = [normalize_rom_title(name) for name in files_in_directory]
    map_orig: dict = {}
    for cleaned, orig in zip(files_cleaned, files_in_directory):
        map_orig.setdefault(cleaned, []).append(orig)

    # Fuzzy match: each keep-list entry → best matching cleaned filename
    best_matches = file_matching(keep_list, files_cleaned)

    files_to_keep = set()
    for name, (cleaned_fn, score) in best_matches.items():
        if score >= args.threshold:
            for orig in map_orig[cleaned_fn]:
                files_to_keep.add(orig)

    files_to_delete = [f for f in files_in_directory if f not in files_to_keep]

    if files_to_keep:
        print("The following files will be kept:")
        for f in sorted(files_to_keep):
            print(f"  {f}")
    else:
        print("No files match the keep list. All files will be deleted.")

    if args.dry_run:
        if files_to_delete:
            print(f"\nDry run: {len(files_to_delete)} file(s) would be deleted.")
        else:
            print("\nDry run: No files to delete.")
        return

    if files_to_delete:
        if confirm_action():
            for f in files_to_delete:
                os.remove(os.path.join(args.directory, f))
            n = len(files_to_delete)
            print(f"\n{n} unmatched file{'s' if n > 1 else ''} deleted.")
        else:
            print("\nOperation cancelled.")
    else:
        print("\nNo files to delete. All files match the keep list.")


if __name__ == "__main__":
    main()
