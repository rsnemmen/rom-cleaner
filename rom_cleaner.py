#!/usr/bin/env python3
"""Convention-aware ROM cleaner CLI."""

from __future__ import annotations

import argparse
import os

from rom_naming import (
    ALL_REGIONS,
    SUPPORTED_CONVENTIONS,
    VERSION,
    delete_path,
    format_bytes,
    parse_rom_name,
    should_keep,
)

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
RESET = "\033[0m"


def _parse_regions(regions_str: str) -> frozenset[str]:
    parts = {r.strip().lower() for r in regions_str.split(",")}
    unknown = parts - ALL_REGIONS
    if unknown:
        raise ValueError(
            f"Unknown region(s): {', '.join(sorted(unknown))}. "
            f"Valid: {', '.join(sorted(ALL_REGIONS))}"
        )
    return frozenset(parts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Keep only preferred ROM variants using filename conventions.",
    )
    parser.add_argument("--version", action="version", version=f"rom-cleaner {VERSION}")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be kept or deleted without making any changes.",
    )
    parser.add_argument(
        "--homebrew",
        action="store_true",
        help='Also delete homebrew files (those with " by Author" in the name).',
    )
    parser.add_argument(
        "--convention",
        choices=SUPPORTED_CONVENTIONS,
        default="goodtools",
        help="Filename convention to interpret (default: goodtools).",
    )
    parser.add_argument(
        "--regions",
        default="usa",
        metavar="REGIONS",
        help="Comma-separated regions to keep (default: usa). Example: --regions usa,japan,europe",
    )
    parser.add_argument(
        "--trash",
        action="store_true",
        help="Send deleted files to the system trash instead of permanently removing them.",
    )
    parser.add_argument("directory", help="Directory containing ROM files.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        parser.error(f"Directory '{args.directory}' does not exist.")

    try:
        keep_regions = _parse_regions(args.regions)
    except ValueError as exc:
        parser.error(str(exc))
        return 1

    if args.trash:
        from rom_naming import send2trash as _st
        if _st is None:
            parser.error("--trash requires send2trash: pip install send2trash")
            return 1

    kept = 0
    deleted = 0
    errors = 0
    bytes_freed = 0

    for rom in sorted(os.listdir(args.directory)):
        rom_path = os.path.join(args.directory, rom)
        if not os.path.isfile(rom_path):
            continue

        parsed = parse_rom_name(rom, convention=args.convention)
        keep = should_keep(parsed, include_homebrew=args.homebrew, keep_regions=keep_regions)

        if keep:
            print(f"{GREEN}Keeping:{RESET} {rom}")
            kept += 1
            continue

        file_size = os.path.getsize(rom_path)
        print(f"{RED}Deleting:{RESET} {rom}")
        if not args.dry_run:
            try:
                delete_path(rom_path, trash=args.trash)
                deleted += 1
                bytes_freed += file_size
            except OSError as exc:
                print(f"{YELLOW}Warning:{RESET} could not delete {rom}: {exc}")
                errors += 1
        else:
            deleted += 1
            bytes_freed += file_size

    parts = [f"Kept: {kept}", f"Deleted: {deleted} ({format_bytes(bytes_freed)})", f"Errors: {errors}"]
    print(" | ".join(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
