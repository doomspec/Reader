# Reader

A command-line tool for reading long documents with support for Markdown, LaTeX, and PDF files.

## Features

- **Preview Mode**: Extracts and displays key sections (headings, code blocks, figures, tables, equations) with context
- **Scope Mode**: Read specific character ranges with character positions
- **File Format Support**: Markdown (.md), LaTeX (.tex), and PDF (.pdf) files
- **PDF to Markdown Conversion**: Automatically converts PDFs to markdown using SuperReader API
- **Smart Caching**: PDF conversions are cached in `.reader` folders for fast subsequent access
- **Enhanced ls Command**: Smart directory listing that shows reader usage hints when document files are present

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
reader research.pdf
```

The preview extracts important elements:
- **Markdown**: Headings (#, ##, ###) and code blocks (```)
- **LaTeX**: Sections (\section, \subsection), figures, tables, and equations
- **PDF**: Automatically converts to markdown first, then extracts key sections

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

# Read specific section of a PDF (uses cached markdown)
reader research.pdf -s 500 1500
```

### PDF Support

PDFs are automatically converted to markdown using the SuperReader API:

```bash
# First time: Converts PDF to markdown and caches it
reader research.pdf

# Subsequent reads: Uses cached markdown (instant)
reader research.pdf

# Force refresh the cache (if PDF was updated)
reader research.pdf -f
```

**Cache Location**: Converted markdown files are stored in `.reader/` folders next to the original PDFs:
```
papers/
├── research.pdf
└── .reader/
    ├── research.md         # Cached markdown
    └── research.meta.json  # Metadata (hash, settings)
```

The cache is automatically validated using file hashes, so updates to the PDF will trigger a fresh conversion.

### Enhanced ls Command

The `reader-ls` command enhances directory listings with reader usage hints:

```bash
reader-ls        # Shows files + reader hints for .md/.tex/.pdf files
reader-ls -lah   # Works with all standard ls flags
```

To override the system `ls` command, add an alias to your shell:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ls='reader-ls'
```

## MCP Server (Model Context Protocol)

The reader tool can also run as an MCP server, allowing AI assistants like Claude to read and analyze documents.

### Running with uvx

```bash
uvx reader-mcp
```

### Claude Desktop Configuration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "reader": {
      "command": "uvx",
      "args": ["reader-mcp"]
    }
  }
}
```

### Using the MCP Tool

Once configured, Claude can use the `reader` tool to:
- Preview documents: `{"filepath": "document.md"}`
- Read specific ranges: `{"filepath": "paper.tex", "scope": [1, 50]}`
- Search for patterns: `{"filepath": "research.pdf", "find": "methodology"}`
- Force refresh PDFs: `{"filepath": "paper.pdf", "force_refresh": true}`

The MCP tool accepts the same parameters as the command-line interface.

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
├── preview.py       # Preview and scope reading logic
├── pdf.py           # PDF to markdown conversion and caching
└── server.py        # MCP server implementation
```

## Development

The tool is inspired by the agentic reader architecture from the El-Agente-Math project, adapted for command-line use with simplified preview functionality.

## Requirements

- Python >= 3.10
- `requests` library (for PDF conversion via SuperReader API)
- `mcp` library (for MCP server functionality)

## License

MIT
