# ROM cleaner

Do you have a large collection of thousands of ROMs? Do you wish there were simple tools to clean and organize it? What if you only want to keep the "Top 50" games in this list?

This is a set of programs for solving these issues. It has two basic tools:

- `rom-cleaner`: keeps only the essential ROMs and discards betas, bad dumps, hacks etc
- `keep-top`: given a list of games, it parses all ROMs and removes everything which is not in the list

## Requirements

- Bash (macOS/Linux built-in; on Windows use Git Bash or Cygwin)
- Python 3.9+ and pip

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

To run the automated tests:

```bash
pip install -r requirements.txt -r requirements-dev.txt
python3 -m pytest
```

## Download

```bash
git clone https://github.com/rsnemmen/rom-cleaner.git
chmod u+x rom-cleaner.sh parse-dirs.sh
```

## Use cases

### Case study 1

`rom-cleaner` now understands both [GoodTools](https://segaretro.org/GoodTools) filenames and No-Intro-style filenames. GoodTools keeps its old behavior by default, and you can opt into other parsing rules with `--convention`.

Suppose you have the following Super Nintendo ROMs in a directory named `SNES`:

```
Aladdin [E].smc
Aladdin [F].smc
Aladdin [J] [!].smc
Aladdin [U][b1].smc
Aladdin [U] [!].smc
```

You want to remove the European, French, and bad-dump versions, leaving only the US verified dump. Run:

```bash
./rom-cleaner.sh --dry-run SNES   # preview first
./rom-cleaner.sh SNES             # then delete
```

This keeps `Aladdin [U] [!].smc` and deletes the rest. Note that `[b1]` (bad dump) is now explicitly detected and deleted even when combined with a region tag like `[U]`. To also keep the Japanese release, pass `--regions usa,japan`.

## `rom-cleaner`

Shell wrapper around a shared Python parser. It understands the following conventions:

- `goodtools` — square-bracket tags like `[U]` and `[!]` (default)
- `no-intro` — parenthetical tags like `(USA)` and `(Beta)`
- `auto` — applies both parsers, useful for mixed collections

### Keep policy

Bad quality dumps are always deleted first:

- `[a]`/`[b]`/`[f]`/`[o]`/`[p]`/`[t]` and their numbered variants (`[b1]`, `[o2]`, etc.) — alternate, bad dump, fixed, overdump, pirate, trained

Then hacks and prerelease builds are deleted:

- `[h]`/`[hN]` or `hack` in the filename
- `(Beta)`, `(Proto)`, `(Prototype)`

After that, files are kept if they match any of:

- Region tag in the allowed set (see `--regions`, default: USA)
- `[!]` verified dump with no region tag — treated as a universal release
- No recognized convention tag at all — likely the original release
- Only benign metadata tags: `(Rev N)`, `(Disc N)`, `(v1.1)`, language tags like `(En,Fr,De)` — kept as original-release equivalents

Everything else is deleted.

### Usage

```bash
# Preview only (no changes)
./rom-cleaner.sh --dry-run <roms-dir>

# Delete bad dumps (keeps USA by default)
./rom-cleaner.sh <roms-dir>

# Also keep Japan and Europe
./rom-cleaner.sh --regions usa,japan,europe <roms-dir>

# Parse filenames as No-Intro releases
./rom-cleaner.sh --convention no-intro <roms-dir>

# Apply both GoodTools and No-Intro parsing rules
./rom-cleaner.sh --convention auto <roms-dir>

# Also delete homebrew ("Game by Author" naming)
./rom-cleaner.sh --homebrew <roms-dir>

# Send deleted files to Trash instead of permanently removing them
./rom-cleaner.sh --trash <roms-dir>

# Run across multiple directories at once
./parse-dirs.sh [--dry-run] [--homebrew] [--convention <name>] [--regions <list>] <dir1> <dir2> ...
```

**Note on `--trash`:** on macOS files go to `~/.Trash` via Finder. On Linux they go to `~/.local/share/Trash/`. On WSL, files land in the Linux trash, not the Windows Recycle Bin.

## `keep-top`

Python script. Given a text file of game names (one per line), keeps only the ROM files that fuzzy-match one of those names and deletes everything else.

Matching uses the same shared filename parser as `rom-cleaner`, stripping both GoodTools and No-Intro tags before comparing. That means `aladdin` in your list will still match `Aladdin (U) [!].smc`, and it also matches filenames like `Aladdin (USA) (Rev 1).zip`. Uses `rapidfuzz.WRatio` scoring — tolerant of typos, different word orders, and punctuation differences.

### Usage

```bash
# Preview
python3 keep-top.py <roms-dir> keep.txt --dry-run

# Delete non-matching ROMs (prompts for confirmation)
python3 keep-top.py <roms-dir> keep.txt

# Skip confirmation prompt (for scripting)
python3 keep-top.py <roms-dir> keep.txt --yes

# Send deleted files to Trash
python3 keep-top.py <roms-dir> keep.txt --trash

# Tighten the fuzzy threshold (default is 50, range 0-100)
python3 keep-top.py <roms-dir> keep.txt --threshold 75
```

`keep.txt` format — one game name per line:

```
aladdin
jungle book
super mario world
```
