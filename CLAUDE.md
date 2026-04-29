# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Two tools for pruning large ROM collections:

- **`rom-cleaner.sh`** — bash script that deletes bad dumps, hacks, betas, and regional variants the user doesn't want, keeping only `[!]` (verified good dump), `[U]` (US), `[J]` (Japan), and untagged ROMs.
- **`keep-top.py`** — Python 3 script that deletes any ROM not matching a user-supplied game list (`keep.txt`), using case-insensitive substring matching.
- **`parse-dirs.sh`** — wrapper that runs `rom-cleaner.sh` across multiple directories; hardcodes an absolute install path (`ROM_CLEANER_PATH`), so update that variable if the repo moves.

## Running the tools

```bash
# Preview without deleting anything
./rom-cleaner.sh --dry-run <roms-dir>

# Delete bad dumps (keeps [!], [U], [J], untagged)
./rom-cleaner.sh <roms-dir>

# Also delete homebrew ("by <author>" in filename)
./rom-cleaner.sh --homebrew <roms-dir>

# Keep only games listed in keep.txt (dry-run first!)
python3 keep-top.py <roms-dir> keep.txt --dry-run
python3 keep-top.py <roms-dir> keep.txt

# Run rom-cleaner across multiple directories at once
./parse-dirs.sh [--dry-run] [--homebrew] <dir1> <dir2> ...
```

## Key logic

`rom-cleaner.sh` applies conditions in order; later conditions override earlier ones. The final `[Hh]ack` check always forces `keep=false` regardless of earlier matches. It only processes files in the top-level directory (no recursion).

`keep-top.py` prompts for confirmation before deletion and skips subdirectories. The keep list file is one game name per line; any ROM whose filename contains that string (case-insensitive) is retained.
