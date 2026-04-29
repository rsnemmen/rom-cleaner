# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Two tools for pruning large ROM collections:

- **`rom-cleaner.sh`** — bash script that deletes bad dumps, hacks, betas, and regional variants the user doesn't want, keeping only `[!]` (verified good dump), `[U]`/`[u]` (US), `[J]`/`[j]` (Japan), and untagged ROMs.
- **`keep-top.py`** — Python 3 script that deletes any ROM not fuzzy-matching a user-supplied game list (`keep.txt`), using `rapidfuzz.WRatio` via the `fuzzycp` package. The `fuzzycp` dependency is pinned in `requirements.txt` as a file:// URL to the sibling repo; install with `pip install -r requirements.txt` (or `pip install -e /path/to/fuzzy_cp` directly).
- **`parse-dirs.sh`** — wrapper that runs `rom-cleaner.sh` across multiple directories; uses script-relative path resolution so it works regardless of where the repo is cloned.

## Running the tools

```bash
# Preview without deleting anything
./rom-cleaner.sh --dry-run <roms-dir>

# Delete bad dumps (keeps [!], [U]/[u], [J]/[j], untagged)
./rom-cleaner.sh <roms-dir>

# Also delete homebrew ("by <author>" in filename)
./rom-cleaner.sh --homebrew <roms-dir>

# Run rom-cleaner across multiple directories at once
./parse-dirs.sh [--dry-run] [--homebrew] <dir1> <dir2> ...

# Keep only games listed in keep.txt — always dry-run first
python3 keep-top.py <roms-dir> keep.txt --dry-run
python3 keep-top.py <roms-dir> keep.txt

# Tighten fuzzy threshold (default 50, range 0-100)
python3 keep-top.py <roms-dir> keep.txt --threshold 75
```

## Key logic

`rom-cleaner.sh` evaluates conditions with early-exit for hacks and betas: anything matching `[Hh]ack` or `(Beta)` is deleted immediately, before the tag checks run. This means `[!]` or `[U]` cannot override a hack/beta label. After that filter, `[!]`, `[U]`/`[u]`, `[J]`/`[j]`, and untagged files are kept. Only top-level files are processed (no recursion). Note: the `[Hh]ack` check matches the literal word only — GoodTools shorthand like `[h1]`/`[h2]` is not detected, so `Aladdin [U] [h1].smc` is kept because of the `[U]` tag.

`keep-top.py` uses `fuzzycp.preprocessing()` to strip region/dump tags from candidate filenames before matching, so `aladdin` in `keep.txt` matches `Aladdin (U) [!].smc`. Multiple ROM variants that share the same cleaned stem (e.g. `Aladdin (U) [!].smc` and `Aladdin (J).smc` both clean to `Aladdin`) are all kept when any one of them matches. Prompts for confirmation before deletion. Skips subdirectories.
