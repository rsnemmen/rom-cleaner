 ROM cleaner
 =============

The purpose of this script is to clean a ROM collection, discarding modifications, bad dumps, hacks and betas. It will keep only files that include in the filename: 

- `[!]`: Indicates a good, verified dump. You generally want to keep these versions.
- No tag: If there is no extra tag, the ROM is likely the original version.
- `[U]` for the US or `[J]` for Japan.

## How to use

You need to open a terminal in Linux or MacOS and issue the following commands.

### Download the tool

    git clone https://github.com/rsnemmen/rom-cleaner.git
    chmod u+x rom-cleaner.sh

### Check which files it will keep

Without changing anything.

    rom-cleaner --dry-run <directory-with-ROMs>

### Keep only good ROMs

Notice that this will delete files the tool judges not to be good ROMs. Be careful.

    rom-cleaner <directory-with-ROMs>
