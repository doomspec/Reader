"""
Preview and scope reading functionality for documents.
"""

import os
import re
from dataclasses import dataclass
from typing import Literal

initial_range_size = (-50, 1000)  # (chars before, chars after) for context
min_chars = 1000 * 10
max_chars = 3000 * 10

@dataclass
class KeyPosition:
    """Represents a key position in the document."""
    type: Literal['heading', 'section', 'figure', 'table', 'equation', 'code_block']
    start_line: int
    end_line: int
    content: str
    char_start: int
    char_end: int


def _adjust_range_size(current_preview_len: int, current_range: tuple[int, int],
                       content_len: int) -> tuple[int, int] | None:
    """
    Adjust range size based on current preview length.

    Args:
        current_preview_len: Length of the current preview
        current_range: Current (chars_before, chars_after) as (negative, positive)
        content_len: Total length of the content

    Returns:
        New range size or None if we should stop (range covers whole document)
    """
    chars_before = abs(current_range[0])
    chars_after = current_range[1]

    # Check if range already covers the whole document
    if chars_before >= content_len and chars_after >= content_len:
        return None

    if current_preview_len < min_chars:
        # Need to expand - estimate step size
        gap = min_chars - current_preview_len
        # Estimate: increase proportionally to the gap
        avg_range = (chars_before + chars_after) / 2
        if avg_range > 0 and current_preview_len > 0:
            # Step = gap / current_len * avg_range * safety_factor
            step = int((gap / current_preview_len) * avg_range * 0.5)
            step = max(step, 100)  # Minimum step
        else:
            step = 500  # Default step if we can't estimate

        new_before = min(chars_before + step, content_len)
        new_after = min(chars_after + step, content_len)
        return (-new_before, new_after)

    elif current_preview_len > max_chars:
        # Need to shrink - estimate step size
        gap = current_preview_len - max_chars
        avg_range = (chars_before + chars_after) / 2
        if avg_range > 0 and current_preview_len > 0:
            # Step = gap / current_len * avg_range * safety_factor
            step = int((gap / current_preview_len) * avg_range * 0.5)
            step = max(step, 50)  # Minimum step
        else:
            step = 200  # Default step

        new_before = max(chars_before - step, 10)  # Keep minimum context
        new_after = max(chars_after - step, 50)
        return (-new_before, new_after)

    return current_range  # Size is good


def _generate_merged_ranges(content: str, key_positions: list[KeyPosition],
                            range_size: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Generate merged character ranges for preview.

    Args:
        content: The document content
        key_positions: List of key positions found in the document
        range_size: (chars_before, chars_after) tuple

    Returns:
        List of merged (start_char, end_char) tuples
    """
    merged_ranges: list[tuple[int, int]] = []
    chars_before = abs(range_size[0])
    chars_after = range_size[1]

    for pos in key_positions:
        context_start_char = max(0, pos.char_start - chars_before)
        context_end_char = min(len(content), pos.char_end + chars_after)

        if merged_ranges and context_start_char <= merged_ranges[-1][1]:
            merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], context_end_char))
        else:
            merged_ranges.append((context_start_char, context_end_char))

    return merged_ranges


def _format_preview(content: str, merged_ranges: list[tuple[int, int]],
                   filepath: str, original_filepath: str | None = None,
                   scope_flag: str = "--scope") -> str:
    """
    Format the preview output from merged ranges.

    Args:
        content: The document content
        merged_ranges: List of (start_char, end_char) tuples
        filepath: Path to the file
        original_filepath: Original file path for display
        scope_flag: Flag to use in scope command

    Returns:
        Formatted preview string
    """
    preview_parts: list[str] = []
    display_path = os.path.relpath(original_filepath if original_filepath else filepath)

    for char_start, char_end in merged_ranges:
        display_start = char_start + 1
        display_end = char_end
        range_content = content[char_start:char_end]

        preview_parts.append(f"[Characters {display_start}-{display_end}]")
        preview_parts.append('')
        prefix = '...\n' if char_start > 0 else ''
        suffix = '\n...' if char_end < len(content) else ''
        preview_parts.append(prefix + range_content + suffix)
        preview_parts.append('\n---\n')

    return '\n'.join(preview_parts)


def markdown_to_preview(content: str, filepath: str, original_filepath: str | None = None) -> str:
    """
    Convert markdown to a preview by extracting key positions.

    Args:
        content: The markdown content to preview
        filepath: Path to the file being previewed
        original_filepath: Original file path (e.g., PDF path) to display in commands

    Returns:
        Text string containing the preview with character position information
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

    # Adaptive range sizing
    current_range = initial_range_size
    max_iterations = 20  # Prevent infinite loops

    for iteration in range(max_iterations):
        merged_ranges = _generate_merged_ranges(content, key_positions, current_range)
        preview = _format_preview(content, merged_ranges, filepath, original_filepath, "--scope")
        preview_len = len(preview)

        # Check if size is acceptable
        if min_chars <= preview_len <= max_chars:
            return preview

        # Adjust range size
        new_range = _adjust_range_size(preview_len, current_range, len(content))

        # If no adjustment possible, return current preview
        if new_range is None or new_range == current_range:
            return preview

        current_range = new_range

    # Max iterations reached, return last preview
    return preview


def latex_to_preview(content: str, filepath: str, original_filepath: str | None = None) -> str:
    """
    Convert LaTeX to a preview by extracting key positions.

    Args:
        content: The LaTeX content to preview
        filepath: Path to the file being previewed
        original_filepath: Original file path (e.g., PDF path) to display in commands

    Returns:
        Text string containing the preview with character position information
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

    # Adaptive range sizing
    current_range = initial_range_size
    max_iterations = 20  # Prevent infinite loops

    for iteration in range(max_iterations):
        merged_ranges = _generate_merged_ranges(content, key_positions, current_range)

        # Format with different scope flag for LaTeX
        display_path = os.path.relpath(original_filepath if original_filepath else filepath)
        preview = _format_preview(content, merged_ranges, filepath, original_filepath, "-s")
        preview_len = len(preview)

        # Check if size is acceptable
        if min_chars <= preview_len <= max_chars:
            return preview

        # Adjust range size
        new_range = _adjust_range_size(preview_len, current_range, len(content))

        # If no adjustment possible, return current preview
        if new_range is None or new_range == current_range:
            return preview

        current_range = new_range

    # Max iterations reached, return last preview
    return preview


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


