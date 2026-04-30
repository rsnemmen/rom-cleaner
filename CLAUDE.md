# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Two tools for pruning large ROM collections:

- **`rom-cleaner.sh`** — shell wrapper around a Python cleaner that deletes bad dumps, hacks, betas/prototypes, and regional variants the user doesn't want. It supports `goodtools`, `no-intro`, and `auto` parsing modes; `goodtools` remains the default.
- **`keep-top.py`** — Python 3 script that deletes any ROM not fuzzy-matching a user-supplied game list (`keep.txt`), using `rapidfuzz.WRatio` via the `fuzzycp` package. The `fuzzycp` dependency is pulled from `https://github.com/rsnemmen/fuzzy_cp` via `requirements.txt`; install with `pip install -r requirements.txt`.
- **`parse-dirs.sh`** — wrapper that runs `rom-cleaner.sh` across multiple directories; uses script-relative path resolution so it works regardless of where the repo is cloned.

## Running the tools

```bash
# Preview without deleting anything
./rom-cleaner.sh --dry-run <roms-dir>

# Delete bad dumps (default: keeps USA, [!] with no region, untagged)
./rom-cleaner.sh <roms-dir>

# Also keep Japan and Europe
./rom-cleaner.sh --regions usa,japan,europe <roms-dir>

# Parse No-Intro filenames like (USA) and (Japan)
./rom-cleaner.sh --convention no-intro <roms-dir>

# Also delete homebrew ("Game by Author" in filename)
./rom-cleaner.sh --homebrew <roms-dir>

# Send deleted files to Trash instead of permanently removing them
./rom-cleaner.sh --trash <roms-dir>

# Run rom-cleaner across multiple directories at once
./parse-dirs.sh [--dry-run] [--homebrew] [--convention <name>] <dir1> <dir2> ...

# Keep only games listed in keep.txt — always dry-run first
python3 keep-top.py <roms-dir> keep.txt --dry-run
python3 keep-top.py <roms-dir> keep.txt

# Skip confirmation prompt (for scripting)
python3 keep-top.py <roms-dir> keep.txt --yes

# Send deleted files to Trash
python3 keep-top.py <roms-dir> keep.txt --trash

# Tighten fuzzy threshold (default 50, range 0-100)
python3 keep-top.py <roms-dir> keep.txt --threshold 75
```

## Key logic

`rom-cleaner.sh` delegates filename parsing to shared Python helpers so both `rom-cleaner` and `keep-top.py` interpret tags consistently.

`rom_naming.py` exposes `ParsedRomName` (the parsed result) and `should_keep`. Key fields:
- `is_bad_quality` — `[a]`/`[b]`/`[f]`/`[o]`/`[p]`/`[t]` and numbered variants; always deleted, overrides region and `[!]`
- `is_revision`, `is_disc` — `(Rev N)`, `(Disc N)`; benign metadata, treated like untagged
- `is_language_only_paren`, `has_only_benign_paren_tags` — lang-only tags like `(En,Fr,De)` are also benign
- `is_homebrew` — checked against the post-strip title (case-sensitive), so `Stand By Me` is not flagged

`should_keep` takes a `keep_regions` frozenset (default `{"usa"}`). Files are kept if they match a region in the set, carry `[!]` with no region tag, have no convention tags at all, or have only benign paren tags. Bad-quality, hack, beta, and prototype files are always deleted first.

`keep-top.py` uses the same shared filename normalizer to strip region/dump tags before fuzzy matching. Multiple ROM variants sharing the same cleaned stem are all kept when any one matches. Skips subdirectories.

Both tools print a summary line at the end: `Kept: X | Deleted: Y (Z MB) | Errors: N`.
