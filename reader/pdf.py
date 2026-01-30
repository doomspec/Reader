"""
PDF processing module for converting PDFs to markdown using SuperReader API.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import requests


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
    cache_dir = pdf_dir / '.reader'

    # Create cache directory if it doesn't exist
    cache_dir.mkdir(exist_ok=True)

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
    base_url: str = "https://worker.treer.ai",
    parse_formula: bool = True,
    parse_table: bool = True,
    parse_ocr: bool = True,
    force_refresh: bool = False
) -> str:
    """
    Convert a PDF to markdown, using cache if available.

    Args:
        pdf_path: Path to the PDF file
        base_url: Base URL of the SuperReader API
        parse_formula: Whether to parse formulas
        parse_table: Whether to parse tables
        parse_ocr: Whether to use OCR
        force_refresh: Force refresh the cache

    Returns:
        Path to the markdown file (either cached or newly created)
    """
    cache_path = get_pdf_cache_path(pdf_path)

    # Check cache validity
    if not force_refresh and is_cache_valid(pdf_path, cache_path):
        return str(cache_path)

    # Convert PDF to markdown using SuperReader API
    print(f"Converting PDF to markdown: {Path(pdf_path).name}")
    print("This may take a moment...")

    endpoint = f"{base_url}/pdf_to_markdown"

    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            data = {
                'parse_formula': str(parse_formula).lower(),
                'parse_table': str(parse_table).lower(),
                'parse_ocr': str(parse_ocr).lower()
            }

            response = requests.post(endpoint, files=files, data=data)
            response.raise_for_status()

            result = response.json()
            markdown_content = result.get('markdown', '')

            if not markdown_content:
                raise ValueError("No markdown content returned from API")

            # Save to cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Save metadata
            metadata = {
                'pdf_hash': get_pdf_hash(pdf_path),
                'pdf_path': str(Path(pdf_path).resolve()),
                'parse_formula': parse_formula,
                'parse_table': parse_table,
                'parse_ocr': parse_ocr,
                'api_version': result.get('version', 'unknown')
            }

            metadata_path = cache_path.with_suffix('.meta.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            print(f"✓ Markdown saved to: {cache_path}")

            return str(cache_path)

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error calling SuperReader API: {e}")
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
