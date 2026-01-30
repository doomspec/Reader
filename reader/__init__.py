"""
Reader - A command-line tool for reading long documents.

Supports markdown and LaTeX files with preview and scope reading capabilities.
"""

from .preview import generate_preview, read_scope

__all__ = [
    'generate_preview',
    'read_scope',
]

__version__ = '0.1.0'
