# ROM cleaner

Do you have a large collection of thousands of ROMs? Do you wish there were simple tools to clean and organize it? What if you only want to keep the "Top 50" games in this list?

This is a set of programs for solving these issues. It has two basic tools:

- `rom-cleaner`: keeps only the essential ROMs and discards betas, bad dumps, hacks etc
- `keep-top`: given a list of games, it parses all ROMs and removes everything which is not in the list

## Requirements

- Bash (macOS/Linux built-in; on Windows use Git Bash or Cygwin)
- Python 3.6+ and pip

Install the Python dependency for `keep-top`:

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
Aladdin [S][b1].smc
Aladdin [U] [!].smc
```

You want to remove the European, French, and Spanish (bad-dump) versions, leaving only the Japanese and US verified dumps. Run:

```bash
./rom-cleaner.sh --dry-run SNES   # preview first
./rom-cleaner.sh SNES             # then delete
```

This keeps `Aladdin [J] [!].smc` and `Aladdin [U] [!].smc` and deletes the rest.

## `rom-cleaner`

Shell wrapper around a shared Python parser. It understands the following conventions:

- `goodtools` — square-bracket tags like `[U]` and `[!]` (default)
- `no-intro` — parenthetical tags like `(USA)` and `(Beta)`
- `auto` — applies both parsers, useful for mixed collections

Hacks and prerelease builds such as betas and prototypes are always deleted, regardless of other tags. After that filter, files are kept if they match any of:

- `[!]` — verified good dump
- `[U]` or `[u]` — US release
- `[J]` or `[j]` — Japan release
- `(USA)` — No-Intro US release
- `(Japan)` — No-Intro Japan release
- No recognized convention tag at all — likely the original release

Other variants are deleted unless they carry one of the allowed keep markers above.

### Usage

```bash
# Preview only (no changes)
./rom-cleaner.sh --dry-run <roms-dir>

# Delete bad dumps
./rom-cleaner.sh <roms-dir>

# Parse filenames as No-Intro releases
./rom-cleaner.sh --convention no-intro <roms-dir>

# Apply both GoodTools and No-Intro parsing rules
./rom-cleaner.sh --convention auto <roms-dir>

# Also delete homebrew ("Game by Author" naming)
./rom-cleaner.sh --homebrew <roms-dir>

# Run across multiple directories at once
./parse-dirs.sh [--dry-run] [--homebrew] [--convention <name>] <dir1> <dir2> ...
```

## `keep-top`

Python script. Given a text file of game names (one per line), keeps only the ROM files that fuzzy-match one of those names and deletes everything else.

Matching now uses the same shared filename parser as `rom-cleaner`, stripping both GoodTools and No-Intro tags before comparing. That means `aladdin` in your list will still match `Aladdin (U) [!].smc`, and it also matches filenames like `Aladdin (USA) (Rev 1).zip`. Uses `rapidfuzz.WRatio` scoring — tolerant of typos, different word orders, and punctuation differences.

### Usage

```bash
# Preview
python3 keep-top.py <roms-dir> keep.txt --dry-run

# Delete non-matching ROMs (prompts for confirmation)
python3 keep-top.py <roms-dir> keep.txt

# Tighten the fuzzy threshold (default is 50, range 0-100)
python3 keep-top.py <roms-dir> keep.txt --threshold 75
```

`keep.txt` format — one game name per line:

```
aladdin
jungle book
super mario world
```
