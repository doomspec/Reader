"""
Reader - A command-line tool for reading long documents.

Supports markdown, LaTeX, and PDF files with preview and scope reading capabilities.
Also available as an MCP (Model Context Protocol) server for use with AI assistants.
"""

from .preview import generate_preview, read_scope
from .pdf import pdf_to_markdown, get_or_convert_pdf

__all__ = [
    'generate_preview',
    'read_scope',
    'pdf_to_markdown',
    'get_or_convert_pdf',
]

__version__ = '0.1.0'
