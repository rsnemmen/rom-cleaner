# ROM cleaner

Do you have a large collection of thousands of ROMs? Do you wish there were simple tools to clean and organize it? What if you only want to keep the "Top 50" games in this list?

This is a set of programs for solving these issues. It has two basic tools:

- `rom-cleaner`: keeps only the essential ROMs and discards betas, bad dumps, hacks etc
- `keep-top`: given a list of games, it parses all ROMs and removes everything which is not in the list

## Requirements

- Bash (macOS/Linux built-in; on Windows use Git Bash or Cygwin)
- Python 3.6+ and `fuzzycp` for `keep-top`:

```bash
git clone https://github.com/rsnemmen/fuzzy_cp.git
pip install -e fuzzy_cp
```

Or if you already have the sibling repo:

```bash
pip install -e /path/to/fuzzy_cp
```

## Download

```bash
git clone https://github.com/rsnemmen/rom-cleaner.git
chmod u+x rom-cleaner.sh parse-dirs.sh
```

## Use cases

### Case study 1

`rom-cleaner` recognises the [GoodTools](https://segaretro.org/GoodTools) naming convention, where region and dump info appear in square brackets. Suppose you have the following Super Nintendo ROMs in a directory named `SNES`:

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

Note: the tool only treats files as hacks if the literal word `hack`/`Hack` appears in the filename. GoodTools shorthand like `[h1]` is not recognised — a file like `Aladdin [U] [h1].smc` would still be kept because of the `[U]` tag.

## `rom-cleaner`

Shell script. Hacks (filenames containing `hack`/`Hack`) and betas (`(Beta)`) are always deleted, regardless of other tags. After that filter, files are kept if they match any of:

- `[!]` — verified good dump
- `[U]` or `[u]` — US release
- `[J]` or `[j]` — Japan release
- No bracketed tag at all — likely the original release

Everything else is deleted: alternate dumps, translations, regional variants other than US/Japan, bad dumps.

### Usage

```bash
# Preview only (no changes)
./rom-cleaner.sh --dry-run <roms-dir>

# Delete bad dumps
./rom-cleaner.sh <roms-dir>

# Also delete homebrew ("Game by Author" naming)
./rom-cleaner.sh --homebrew <roms-dir>

# Run across multiple directories at once
./parse-dirs.sh [--dry-run] [--homebrew] <dir1> <dir2> ...
```

## `keep-top`

Python script. Given a text file of game names (one per line), keeps only the ROM files that fuzzy-match one of those names and deletes everything else.

Matching strips region and dump tags (`(U)`, `[!]`, etc.) from filenames before comparing, so `aladdin` in your list will match `Aladdin (U) [!].smc`. Uses `rapidfuzz.WRatio` scoring — tolerant of typos, different word orders, and punctuation differences.

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
