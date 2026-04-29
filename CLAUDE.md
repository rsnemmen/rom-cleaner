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

# Delete bad dumps (GoodTools default: keeps [!], [U]/[u], [J]/[j], untagged)
./rom-cleaner.sh <roms-dir>

# Parse No-Intro filenames like (USA) and (Japan)
./rom-cleaner.sh --convention no-intro <roms-dir>

# Also delete homebrew ("by <author>" in filename)
./rom-cleaner.sh --homebrew <roms-dir>

# Run rom-cleaner across multiple directories at once
./parse-dirs.sh [--dry-run] [--homebrew] [--convention <name>] <dir1> <dir2> ...

# Keep only games listed in keep.txt — always dry-run first
python3 keep-top.py <roms-dir> keep.txt --dry-run
python3 keep-top.py <roms-dir> keep.txt

# Tighten fuzzy threshold (default 50, range 0-100)
python3 keep-top.py <roms-dir> keep.txt --threshold 75
```

## Key logic

`rom-cleaner.sh` now delegates filename parsing to shared Python helpers so both `rom-cleaner` and `keep-top.py` interpret tags consistently. In `goodtools` mode it preserves the existing keep policy for `[!]`, `[U]`/`[u]`, `[J]`/`[j]`, and untagged files, while also understanding shorthand hack tags like `[h1]`. In `no-intro` mode it recognises parenthetical region tags like `(USA)` and `(Japan)`, and prerelease tags like `(Beta)` and `(Proto)`. Only top-level files are processed (no recursion).

`keep-top.py` uses the same shared filename normalizer as `rom-cleaner.sh` to strip region/dump tags from candidate filenames before matching, so `aladdin` in `keep.txt` matches both `Aladdin (U) [!].smc` and `Aladdin (USA) (Rev 1).zip`. Multiple ROM variants that share the same cleaned stem are all kept when any one of them matches. Prompts for confirmation before deletion. Skips subdirectories.
