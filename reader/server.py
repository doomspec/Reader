"""
MCP server for the reader tool.

Exposes reader functionality as an MCP tool that can be called by Claude and other AI assistants.
"""

import sys
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .preview import generate_preview, read_scope, find_in_document
from .pdf import get_or_convert_pdf


# Create the MCP server
app = Server("reader")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="read",
            description=(
                "Read and preview long documents (markdown, LaTeX, and PDF files). "
                "Will return an indexing of the document if no scope is specified. You can also read specific character ranges, or search for patterns. "
                "Supports .md, .tex, and .pdf files."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the document file (.md, .tex, or .pdf)"
                    },
                    "scope": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Read specific character range [start, end] (e.g., [1, 50])"
                    },
                    "find": {
                        "type": "string",
                        "description": "Search for regex pattern in the document (returns -50 to +100 chars around first 20 matches)"
                    }
                },
                "required": ["filepath"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name != "read":
        raise ValueError(f"Unknown tool: {name}")

    filepath_str = arguments.get("filepath")
    if not filepath_str:
        raise ValueError("filepath is required")

    # Check if file exists
    filepath = Path(filepath_str)
    if not filepath.exists():
        raise ValueError(f"File not found: {filepath_str}")

    # Check file extension
    if filepath.suffix not in ['.md', '.tex', '.pdf']:
        raise ValueError(f"Unsupported file type. Only .md, .tex, and .pdf files are supported.")

    try:
        # Handle PDF files by converting to markdown first
        working_filepath = str(filepath)
        original_filepath = None
        if filepath.suffix == '.pdf':
            try:
                original_filepath = str(filepath)
                force_refresh = arguments.get("force_refresh", False)
                working_filepath = get_or_convert_pdf(
                    str(filepath),
                    force_refresh=force_refresh
                )
            except Exception as e:
                raise ValueError(f"Error processing PDF: {e}")

        # Now process the (possibly converted) file
        scope = arguments.get("scope")
        find_pattern = arguments.get("find")

        if scope:
            if not isinstance(scope, list) or len(scope) != 2:
                raise ValueError("scope must be an array of two integers [start, end]")
            start_char, end_char = scope
            output = read_scope(working_filepath, start_char, end_char)
        elif find_pattern:
            output = find_in_document(
                working_filepath,
                find_pattern,
                original_filepath=original_filepath
            )
        else:
            output = generate_preview(working_filepath)

        return [TextContent(type="text", text=output)]

    except Exception as e:
        raise ValueError(f"Error: {e}")


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Synchronous entry point for the server."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    run()
