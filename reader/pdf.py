"""
PDF processing module for converting PDFs to markdown using MinerU.
"""

import os
import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any


def get_pdf_cache_path(pdf_path: str) -> Path:
    """
    Get the cache path for a PDF file's markdown version.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Path to the cached markdown file
    """
    pdf_file = Path(pdf_path).resolve()
    pdf_dir = pdf_file.parent
    cache_dir = pdf_dir / '.reader' / pdf_file.stem

    # Create cache directory if it doesn't exist
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Use the PDF filename (without extension) for the cached markdown
    cached_file = cache_dir / f"{pdf_file.stem}.md"

    return cached_file


def get_pdf_hash(pdf_path: str) -> str:
    """
    Calculate SHA256 hash of PDF file to detect changes.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Hex digest of the file hash
    """
    hash_sha256 = hashlib.sha256()
    with open(pdf_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def is_cache_valid(pdf_path: str, cache_path: Path) -> bool:
    """
    Check if the cached markdown is still valid for the PDF.

    Args:
        pdf_path: Path to the PDF file
        cache_path: Path to the cached markdown file

    Returns:
        True if cache is valid, False otherwise
    """
    if not cache_path.exists():
        return False

    # Check if metadata file exists
    metadata_path = cache_path.with_suffix('.meta.json')
    if not metadata_path.exists():
        return False

    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Compare hash
        current_hash = get_pdf_hash(pdf_path)
        return metadata.get('pdf_hash') == current_hash
    except (json.JSONDecodeError, KeyError):
        return False


def pdf_to_markdown(
    pdf_path: str,
    force_refresh: bool = False
) -> str:
    """
    Convert a PDF to markdown using MinerU, using cache if available.

    Args:
        pdf_path: Path to the PDF file
        force_refresh: Force refresh the cache

    Returns:
        Path to the markdown file (either cached or newly created)
    """
    cache_path = get_pdf_cache_path(pdf_path)

    # Check cache validity
    if not force_refresh and is_cache_valid(pdf_path, cache_path):
        return str(cache_path)

    # Convert PDF to markdown using MinerU
    pdf_file = Path(pdf_path).resolve()
    pdf_dir = pdf_file.parent
    print(f"Converting PDF to markdown: {pdf_file.name}")
    print("This may take a moment...")

    try:
        # Use a temp directory in .reader for mineru output
        temp_output_dir = pdf_dir / '.reader' / f".temp_{pdf_file.stem}"
        temp_output_dir.mkdir(parents=True, exist_ok=True)

        # Run mineru command
        cmd = ["mineru", "-p", str(pdf_file), "-o", str(temp_output_dir)]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Find the generated markdown file
        # MinerU typically creates a subdirectory with the PDF name
        pdf_stem = pdf_file.stem
        possible_paths = [
            temp_output_dir / pdf_stem / f"{pdf_stem}.md",
            temp_output_dir / f"{pdf_stem}.md",
            temp_output_dir / "output.md",
        ]

        # Also search for any .md files in the output directory
        markdown_files = list(temp_output_dir.rglob("*.md"))

        markdown_file = None
        source_dir = None
        for path in possible_paths:
            if path.exists():
                markdown_file = path
                source_dir = path.parent
                break

        # If not found in expected locations, use the most recently created .md file
        if not markdown_file and markdown_files:
            markdown_file = max(markdown_files, key=lambda p: p.stat().st_mtime)
            source_dir = markdown_file.parent

        if not markdown_file or not markdown_file.exists():
            raise FileNotFoundError(
                f"Could not find generated markdown file in {temp_output_dir}"
            )

        # Get the cache directory (parent of cache_path)
        cache_dir = cache_path.parent

        # Copy the markdown file to cache
        shutil.copy2(markdown_file, cache_path)

        # Copy all associated files (images, etc.) to the cache directory
        # This ensures image references in the markdown work correctly
        for item in source_dir.iterdir():
            if item.is_file() and item != markdown_file:
                # Copy other files (images, etc.)
                dest_file = cache_dir / item.name
                shutil.copy2(item, dest_file)
            elif item.is_dir():
                # Copy directories (like images folder)
                dest_dir = cache_dir / item.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(item, dest_dir)

        # Clean up temp directory
        shutil.rmtree(temp_output_dir)

        # Save metadata
        metadata = {
            'pdf_hash': get_pdf_hash(pdf_path),
            'pdf_path': str(pdf_file),
            'cache_dir': str(cache_dir),
            'converter': 'mineru'
        }

        metadata_path = cache_path.with_suffix('.meta.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Markdown saved to: {cache_path}")

        return str(cache_path)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Error running mineru command: {e}\n"
            f"stdout: {e.stdout}\n"
            f"stderr: {e.stderr}"
        )
    except Exception as e:
        raise RuntimeError(f"Error converting PDF: {e}")


def get_or_convert_pdf(pdf_path: str, force_refresh: bool = False) -> str:
    """
    Get the markdown version of a PDF, converting if necessary.

    Args:
        pdf_path: Path to the PDF file
        force_refresh: Force refresh the cache

    Returns:
        Path to the markdown file
    """
    return pdf_to_markdown(pdf_path, force_refresh=force_refresh)
