"""
Command-line interface for the reader tool.
"""

import sys
import argparse
from pathlib import Path
from .preview import generate_preview, read_scope


def main():
    """Main entry point for the reader CLI."""
    parser = argparse.ArgumentParser(
        prog='reader',
        description='Read and preview long documents (markdown and LaTeX)'
    )

    parser.add_argument(
        'filepath',
        type=str,
        help='Path to the document file (.md or .tex)'
    )

    parser.add_argument(
        '-s', '--scope',
        nargs=2,
        type=int,
        metavar=('START', 'END'),
        help='Read specific character range (e.g., document.md -s 1 50)'
    )

    args = parser.parse_args()

    # Check if file exists
    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)

    # Check file extension
    if not (filepath.suffix == '.md' or filepath.suffix == '.tex'):
        print(f"Error: Unsupported file type. Only .md and .tex files are supported.", file=sys.stderr)
        sys.exit(1)

    try:
        if args.scope:
            start_char, end_char = args.scope
            output = read_scope(str(filepath), start_char, end_char)
        else:
            output = generate_preview(str(filepath))

        print(output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
