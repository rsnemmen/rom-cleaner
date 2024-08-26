 ROM cleaner
 =============

The purpose of this script is to clean a ROM collection, discarding modifications, bad dumps, hacks, betas. Even homebrew versions if you desire so. It will keep only files that include in the filename: 

- `[!]`: Indicates a good, verified dump. You generally want to keep these versions.
- No tag: If there is no extra tag, the ROM is likely the original version.
- `[U]` for the US or `[J]` for Japan.

This script requires a basic knowledge of using the terminal. If you are using a Mac or Linux box, just open the terminal and issue the commands below. If you are windows user, you will have to install either [Git Bash](gitforwindows.org) or [Cygwin](cygwin.com) in order to execute this script. 

## How to use


### Download the tool

    git clone https://github.com/rsnemmen/rom-cleaner.git
    chmod u+x rom-cleaner.sh

### Check without changing anything

By using the `--dry-run` option, the script will not actually change anything in the disk. It will only display the files and the decision to delete or keep for each one.

    rom-cleaner --dry-run <directory-with-ROMs>

### Keep only good ROMs

Warning: this will delete files the tool judges to not be good ROMs. Be careful.

    rom-cleaner <directory-with-ROMs>

### Remove also homebrew versions

    rom-cleaner --homebrew <directory-with-ROMs>
