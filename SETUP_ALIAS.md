# Setting Up ls Override

The `reader-ls` command enhances the standard `ls` by showing helpful reader commands when .md or .tex files are present.

## Quick Setup

### Option 1: Temporary Alias (Current Session Only)

```bash
alias ls='reader-ls'
```

### Option 2: Permanent Alias

Add to your `~/.bashrc` (Bash) or `~/.zshrc` (Zsh):

```bash
# Reader-enhanced ls command
alias ls='reader-ls'
```

Then reload your shell:
```bash
source ~/.bashrc   # for Bash
# or
source ~/.zshrc    # for Zsh
```

### Option 3: Use the Setup Script

```bash
source setup_alias.sh
```

## Usage

After setting up the alias, use `ls` normally:

```bash
ls              # Shows files + reader hints for .md/.tex files
ls -lah         # Works with all standard ls flags
ls Documents/   # Works with directories
```

## Example Output

```
$ ls
README.md
test_example.md
test_example.tex
pyproject.toml

📚 Document files detected!

  Markdown files (2):
    • test_example.md
    • README.md

  LaTeX files (1):
    • test_example.tex

  Quick commands:
    reader test_example.md                    # Preview document
    reader test_example.md -s 1 50            # Read characters 1-50
```

## Reverting to System ls

If you want to use the original `ls` command:

```bash
unalias ls           # Remove the alias
\ls                  # Or prefix with backslash to bypass alias
/bin/ls              # Or use the full path
```

## How It Works

The `reader-ls` command:
1. Runs the system's `/bin/ls` with all your original flags
2. Checks the directory for .md and .tex files
3. If found, displays helpful hints about using the `reader` command
4. Preserves all standard ls functionality and exit codes
