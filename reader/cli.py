"""
Command-line interface for the reader tool.
"""

import sys
import argparse
from pathlib import Path
from .preview import generate_preview, read_scope, find_in_document
from .pdf import get_or_convert_pdf


def main():
    """Main entry point for the reader CLI."""
    parser = argparse.ArgumentParser(
        prog='reader',
        description='Read and preview long documents (markdown, LaTeX, and PDF)'
    )

    parser.add_argument(
        'filepath',
        type=str,
        help='Path to the document file (.md, .tex, or .pdf)'
    )

    parser.add_argument(
        '-s', '--scope',
        nargs=2,
        type=int,
        metavar=('START', 'END'),
        help='Read specific character range (e.g., document.md -s 1 50)'
    )

    parser.add_argument(
        '-f', '--find',
        type=str,
        metavar='PATTERN',
        help='Search for regex pattern in the document (returns -50 to +100 chars around first 20 matches)'
    )

    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force refresh the PDF cache (only for PDF files)'
    )

    args = parser.parse_args()

    # Check if file exists
    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)

    # Check file extension
    if not (filepath.suffix in ['.md', '.tex', '.pdf']):
        print(f"Error: Unsupported file type. Only .md, .tex, and .pdf files are supported.", file=sys.stderr)
        sys.exit(1)

    try:
        # Handle PDF files by converting to markdown first
        working_filepath = str(filepath)
        original_filepath = None
        if filepath.suffix == '.pdf':
            try:
                original_filepath = str(filepath)
                working_filepath = get_or_convert_pdf(
                    str(filepath),
                    force_refresh=args.force_refresh
                )
            except Exception as e:
                print(f"Error processing PDF: {e}", file=sys.stderr)
                sys.exit(1)

        # Now process the (possibly converted) file
        if args.scope:
            start_char, end_char = args.scope
            output = read_scope(working_filepath, start_char, end_char)
        elif args.find:
            output = find_in_document(
                working_filepath,
                args.find,
                original_filepath=original_filepath
            )
        else:
            output = generate_preview(working_filepath)

        print(output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
