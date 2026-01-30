"""
Preview and scope reading functionality for documents.
"""

import re
from dataclasses import dataclass
from typing import Literal


@dataclass
class KeyPosition:
    """Represents a key position in the document."""
    type: Literal['heading', 'section', 'figure', 'table', 'equation', 'code_block']
    start_line: int
    end_line: int
    content: str
    char_start: int
    char_end: int


def markdown_to_preview(content: str, filepath: str, lines_context: int = 3) -> str:
    """
    Convert markdown to a preview by extracting key positions.

    Args:
        content: The markdown content to preview
        filepath: Path to the file being previewed
        lines_context: Number of lines to show around each key position (default: 3)

    Returns:
        Text string containing the preview with line number information
    """
    lines = content.split('\n')
    key_positions: list[KeyPosition] = []

    char_position = 0
    for i, line in enumerate(lines, start=1):
        line_start_char = char_position
        line_end_char = char_position + len(line)
        char_position = line_end_char + 1  # +1 for newline

        # Find headings (# ## ###)
        if line.strip().startswith('#'):
            key_positions.append(KeyPosition(
                type='heading',
                start_line=i,
                end_line=i,
                content=line,
                char_start=line_start_char,
                char_end=line_end_char
            ))

        # Find code blocks (```)
        elif line.strip().startswith('```'):
            # Find the closing ```
            for j in range(i, len(lines) + 1):
                if j > i and lines[j - 1].strip().startswith('```'):
                    end_char = char_position
                    for k in range(i, j):
                        end_char += len(lines[k - 1]) + 1
                    key_positions.append(KeyPosition(
                        type='code_block',
                        start_line=i,
                        end_line=j,
                        content='\n'.join(lines[i-1:j]),
                        char_start=line_start_char,
                        char_end=end_char
                    ))
                    break

    # Generate preview
    preview_parts: list[str] = []
    merged_ranges: list[tuple[int, int]] = []

    for pos in key_positions:
        context_start = max(1, pos.start_line - lines_context)
        context_end = min(len(lines), pos.end_line + lines_context)

        # Merge overlapping ranges
        if merged_ranges and context_start <= merged_ranges[-1][1]:
            merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], context_end))
        else:
            merged_ranges.append((context_start, context_end))

    # Calculate character positions for merged ranges
    for start, end in merged_ranges:
        # Calculate character positions for the line range
        char_start = sum(len(lines[i]) + 1 for i in range(start - 1)) + 1
        char_end = sum(len(lines[i]) + 1 for i in range(end))

        preview_parts.append(f"[Characters {char_start}-{char_end}]")
        preview_parts.append(f"To read this section: reader {filepath} -s {char_start} {char_end}")
        preview_parts.append('')
        prefix = '...\n' if start > 1 else ''
        suffix = '\n...' if end < len(lines) else ''
        preview_parts.append(prefix + '\n'.join(lines[start-1:end]) + suffix)
        preview_parts.append('\n---\n')

    return '\n'.join(preview_parts)


def latex_to_preview(content: str, filepath: str, lines_context: int = 3) -> str:
    """
    Convert LaTeX to a preview by extracting key positions.

    Args:
        content: The LaTeX content to preview
        filepath: Path to the file being previewed
        lines_context: Number of lines to show around each key position (default: 3)

    Returns:
        Text string containing the preview with line number information
    """
    lines = content.split('\n')
    key_positions: list[KeyPosition] = []

    char_position = 0
    for i, line in enumerate(lines, start=1):
        line_start_char = char_position
        line_end_char = char_position + len(line)
        char_position = line_end_char + 1

        # Find sections
        if re.search(r'\\(?:section|subsection|subsubsection|paragraph|subparagraph)\*?\{', line):
            key_positions.append(KeyPosition(
                type='section',
                start_line=i,
                end_line=i,
                content=line,
                char_start=line_start_char,
                char_end=line_end_char
            ))

        # Find begin environments
        elif re.search(r'\\begin\{(?:figure|table|equation|align|gather)\*?\}', line):
            # Find matching end
            env_match = re.search(r'\\begin\{(.*?)\}', line)
            if env_match:
                env_name = env_match.group(1)
                for j in range(i, len(lines) + 1):
                    if re.search(rf'\\end\{{{env_name}\}}', lines[j - 1]):
                        end_char = char_position
                        for k in range(i, j):
                            end_char += len(lines[k - 1]) + 1

                        env_type = 'equation' if env_name in ['equation', 'align', 'gather'] else env_name
                        key_positions.append(KeyPosition(
                            type=env_type,  # type: ignore
                            start_line=i,
                            end_line=j,
                            content='\n'.join(lines[i-1:j]),
                            char_start=line_start_char,
                            char_end=end_char
                        ))
                        break

    # Generate preview
    preview_parts: list[str] = []
    merged_ranges: list[tuple[int, int]] = []

    for pos in key_positions:
        context_start = max(1, pos.start_line - lines_context)
        context_end = min(len(lines), pos.end_line + lines_context)

        # Merge overlapping ranges
        if merged_ranges and context_start <= merged_ranges[-1][1]:
            merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], context_end))
        else:
            merged_ranges.append((context_start, context_end))

    # Calculate character positions for merged ranges
    for start, end in merged_ranges:
        # Calculate character positions for the line range
        char_start = sum(len(lines[i]) + 1 for i in range(start - 1)) + 1
        char_end = sum(len(lines[i]) + 1 for i in range(end))

        preview_parts.append(f"[Characters {char_start}-{char_end}]")
        preview_parts.append(f"To read this section: reader {filepath} -s {char_start} {char_end}")
        preview_parts.append('')
        prefix = '...\n' if start > 1 else ''
        suffix = '\n...' if end < len(lines) else ''
        preview_parts.append(prefix + '\n'.join(lines[start-1:end]) + suffix)
        preview_parts.append('\n---\n')

    return '\n'.join(preview_parts)


def generate_preview(filepath: str) -> str:
    """
    Generate a preview for the given file.

    Args:
        filepath: Path to the document file

    Returns:
        Preview text with line numbers
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if filepath.endswith('.md'):
        return markdown_to_preview(content, filepath)
    elif filepath.endswith('.tex'):
        return latex_to_preview(content, filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")


def read_scope(filepath: str, start_char: int, end_char: int) -> str:
    """
    Read a specific character range from the file.

    Args:
        filepath: Path to the document file
        start_char: Starting character position (1-indexed)
        end_char: Ending character position (inclusive)

    Returns:
        Text content in the specified character range
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    total_chars = len(content)

    if start_char < 1 or start_char > total_chars:
        raise ValueError(f"Start character {start_char} is out of range (1-{total_chars})")

    if end_char < start_char or end_char > total_chars:
        raise ValueError(f"End character {end_char} is out of range ({start_char}-{total_chars})")

    # Convert to 0-indexed
    result = content[start_char - 1:end_char]

    return result
