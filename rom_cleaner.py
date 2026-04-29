#!/usr/bin/env python3
"""Convention-aware ROM cleaner CLI."""

from __future__ import annotations

import argparse
import os

from rom_naming import SUPPORTED_CONVENTIONS, parse_rom_name, should_keep

GREEN = "\033[0;32m"
RED = "\033[0;31m"
RESET = "\033[0m"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Keep only preferred ROM variants using filename conventions.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be kept or deleted without making any changes.",
    )
    parser.add_argument(
        "--homebrew",
        action="store_true",
        help='Also delete homebrew files that include " by " in the filename.',
    )
    parser.add_argument(
        "--convention",
        choices=SUPPORTED_CONVENTIONS,
        default="goodtools",
        help="Filename convention to interpret (default: goodtools).",
    )
    parser.add_argument("directory", help="Directory containing ROM files.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        parser.error(f"Directory '{args.directory}' does not exist.")

    for rom in sorted(os.listdir(args.directory)):
        rom_path = os.path.join(args.directory, rom)
        if not os.path.isfile(rom_path):
            continue

        parsed = parse_rom_name(rom, convention=args.convention)
        keep = should_keep(parsed, include_homebrew=args.homebrew)

        if keep:
            print(f"{GREEN}Keeping:{RESET} {rom}")
            continue

        print(f"{RED}Deleting:{RESET} {rom}")
        if not args.dry_run:
            os.remove(rom_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
