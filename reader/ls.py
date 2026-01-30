"""
Custom ls command that provides reader usage hints for .md and .tex files.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Custom ls command with reader hints."""
    # Get the arguments passed to our ls command
    args = sys.argv[1:]

    # Find the system ls command (not our wrapper)
    # Use /bin/ls to ensure we get the real system ls
    system_ls = '/bin/ls'

    # Run the system ls command with all the original arguments
    try:
        # Pass through all arguments and run system ls
        result = subprocess.run(
            [system_ls] + args,
            capture_output=False,
            text=True
        )
        exit_code = result.returncode
    except Exception as e:
        print(f"Error running ls: {e}", file=sys.stderr)
        sys.exit(1)

    # After ls runs, check for .md and .tex files in the current directory
    # (or specified directory if provided)
    target_dir = '.'

    # Parse arguments to find if a directory was specified
    # Simple parsing: if last arg doesn't start with -, treat it as directory
    if args:
        # Check if any positional argument (non-flag) exists
        for arg in args:
            if not arg.startswith('-') and os.path.isdir(arg):
                target_dir = arg
                break

    # Look for .md, .tex, and .pdf files
    try:
        md_files = list(Path(target_dir).glob('*.md'))
        tex_files = list(Path(target_dir).glob('*.tex'))
        pdf_files = list(Path(target_dir).glob('*.pdf'))

        if md_files or tex_files or pdf_files:
            print()  # Blank line for separation
            print("You can use reader command for .md, .tex, and .pdf files")
            # Show example with first file found
            example_file = (md_files + tex_files + pdf_files)[0].name
            print(f"    reader {example_file}                    # Preview document")
            print(f"    reader {example_file} -s 1 50            # Read characters 1-50")
            if pdf_files:
                print(f"    reader {pdf_files[0].name} -f            # Force refresh PDF cache")
            print()

    except Exception:
        # Silently ignore errors in file detection
        pass

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
