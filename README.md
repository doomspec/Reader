# Reader

A command-line tool for reading long documents with support for Markdown and LaTeX files.

## Features

- **Preview Mode**: Extracts and displays key sections (headings, code blocks, figures, tables, equations) with context
- **Scope Mode**: Read specific line ranges with line numbers
- **File Format Support**: Markdown (.md) and LaTeX (.tex) files
- **Enhanced ls Command**: Smart directory listing that shows reader usage hints when .md/.tex files are present

## Installation

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Usage

### Preview Mode

Display a preview of the document showing key sections:

```bash
reader document.md
reader paper.tex
```

The preview extracts important elements:
- **Markdown**: Headings (#, ##, ###) and code blocks (```)
- **LaTeX**: Sections (\section, \subsection), figures, tables, and equations

### Scope Mode

Read specific character ranges:

```bash
reader document.md -s START END
```

Examples:
```bash
# Read characters 1 to 50 of a markdown file
reader document.md -s 1 50

# Read characters 100 to 500 of a LaTeX file
reader paper.tex -s 100 500
```

### Enhanced ls Command

The `reader-ls` command enhances directory listings with reader usage hints:

```bash
reader-ls        # Shows files + reader hints for .md/.tex files
reader-ls -lah   # Works with all standard ls flags
```

To override the system `ls` command, add an alias to your shell:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ls='reader-ls'
```

See [SETUP_ALIAS.md](SETUP_ALIAS.md) for detailed setup instructions.

## Examples

### Enhanced ls Output
```bash
$ reader-ls
README.md
test_example.md
test_example.tex

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

### Markdown Preview
```bash
$ reader test_example.md
[Lines 1-12]
# Introduction

This is a test markdown document...

## Background

...
```

### LaTeX Scope Reading
```bash
$ reader paper.tex -s 100 500

\section{Mathematical Background}

Consider the following equation:

\begin{equation}
...
```

## Project Structure

```
reader/
├── __init__.py      # Package initialization
├── cli.py           # Command-line interface (reader command)
├── ls.py            # Enhanced ls command (reader-ls)
└── preview.py       # Preview and scope reading logic
```

## Development

The tool is inspired by the agentic reader architecture from the El-Agente-Math project, adapted for command-line use with simplified preview functionality.

## Requirements

- Python >= 3.13
- No external dependencies required

## License

MIT
