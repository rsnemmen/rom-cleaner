# ROM cleaner

Do you have a large collection of thousands of ROMs? Do you wish there were simple tools to clean and organize it? What if you only want to keep the “Top 50” games in this list?

This is a set of programs for solving these issues. It has two basic tools:

- `rom-cleaner`: keeps only the essential ROMs and discards betas, bad dumps, hacks etc
- `keep-top`: given a list of games, it parses all ROMs and removes everything which is not in the list

## Use cases

### Case study 1: 

Suppose you have the following Super Nintendo ROMs in a directory named `SNES`:

```
Aladdin (E).smc
Aladdin (F).smc
Aladdin (G) [!].smc
Aladdin (J).smc
Aladdin (S) (NG-Dump Known).smc
Aladdin (U) [!].smc
```

Now, you want to remove all files which are hacks, bad dumps, betas etc, leaving only the Japanese and US versions of the games. Here is how you would do so from the command-line:



## Pre-requisites

This script requires a basic knowledge of using the terminal. If you are using a Mac or Linux box, just open the terminal and issue the commands below. If you are windows user, you will have to install either [Git Bash](gitforwindows.org) or [Cygwin](cygwin.com) in order to execute this script. 


## More info

## `rom-cleaner`

shell script 

The purpose of this script is to clean a ROM collection, discarding modifications, bad dumps, hacks, betas. Even homebrew versions if you desire so. It will keep only files that include in the filename: 

- `[!]`: Indicates a good, verified dump. You generally want to keep these versions.
- No tag: If there is no extra tag, the ROM is likely the original version.
- `[U]` for the US or `[J]` for Japan.

## `keep-top`

python script

## Download the tool

    git clone https://github.com/rsnemmen/rom-cleaner.git
    chmod u+x rom-cleaner.sh


## How to use

### Check without changing anything

By using the `--dry-run` option, the script will not actually change anything in the disk. It will only display the files and the decision to delete or keep for each one.

    rom-cleaner --dry-run <directory-with-ROMs>

### Keep only good ROMs

Warning: this will delete files the tool judges to not be good ROMs. Be careful.

    rom-cleaner <directory-with-ROMs>

### Remove also homebrew versions

    rom-cleaner --homebrew <directory-with-ROMs>
