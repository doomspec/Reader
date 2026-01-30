"""
Preview and scope reading functionality for documents.
"""

import os
import re
from dataclasses import dataclass
from typing import Literal

range_size = (-50, 1000)  # (chars before, chars after) for context


@dataclass
class KeyPosition:
    """Represents a key position in the document."""
    type: Literal['heading', 'section', 'figure', 'table', 'equation', 'code_block']
    start_line: int
    end_line: int
    content: str
    char_start: int
    char_end: int


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

    # Generate preview using character-based ranges
    preview_parts: list[str] = []
    merged_ranges: list[tuple[int, int]] = []  # Character ranges

    chars_before = abs(range_size[0])
    chars_after = range_size[1]

    for pos in key_positions:
        # Calculate character range with context
        context_start_char = max(0, pos.char_start - chars_before)
        context_end_char = min(len(content), pos.char_end + chars_after)

        # Merge overlapping ranges
        if merged_ranges and context_start_char <= merged_ranges[-1][1]:
            merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], context_end_char))
        else:
            merged_ranges.append((context_start_char, context_end_char))

    # Display merged character ranges
    display_path = os.path.relpath(original_filepath if original_filepath else filepath)
    for char_start, char_end in merged_ranges:
        # Convert to 1-indexed for display
        display_start = char_start + 1
        display_end = char_end

        # Extract the text content for this range
        range_content = content[char_start:char_end]

        preview_parts.append(f"[Characters {display_start}-{display_end}]")
        preview_parts.append(f"To read this part add: --scope {display_start} {display_end}")
        preview_parts.append('')
        prefix = '...\n' if char_start > 0 else ''
        suffix = '\n...' if char_end < len(content) else ''
        preview_parts.append(prefix + range_content + suffix)
        preview_parts.append('\n---\n')

    return '\n'.join(preview_parts)


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

    # Generate preview using character-based ranges
    preview_parts: list[str] = []
    merged_ranges: list[tuple[int, int]] = []  # Character ranges

    chars_before = abs(range_size[0])
    chars_after = range_size[1]

    for pos in key_positions:
        # Calculate character range with context
        context_start_char = max(0, pos.char_start - chars_before)
        context_end_char = min(len(content), pos.char_end + chars_after)

        # Merge overlapping ranges
        if merged_ranges and context_start_char <= merged_ranges[-1][1]:
            merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], context_end_char))
        else:
            merged_ranges.append((context_start_char, context_end_char))

    # Display merged character ranges
    display_path = os.path.relpath(original_filepath if original_filepath else filepath)
    for char_start, char_end in merged_ranges:
        # Convert to 1-indexed for display
        display_start = char_start + 1
        display_end = char_end

        # Extract the text content for this range
        range_content = content[char_start:char_end]

        preview_parts.append(f"[Characters {display_start}-{display_end}]")
        preview_parts.append(f"To read this section: reader {display_path} -s {display_start} {display_end}")
        preview_parts.append('')
        prefix = '...\n' if char_start > 0 else ''
        suffix = '\n...' if char_end < len(content) else ''
        preview_parts.append(prefix + range_content + suffix)
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


def find_in_document(filepath: str, pattern: str, original_filepath: str | None = None, max_matches: int = 20, context_before: int | None = None, context_after: int | None = None) -> str:
    """
    Find regex pattern matches in the document and return context around each match.

    Args:
        filepath: Path to the document file
        pattern: Regex pattern to search for
        original_filepath: Original file path (e.g., PDF path) to display in output
        max_matches: Maximum number of matches to return (default: 20)
        context_before: Number of characters to show before each match (default: from range_size)
        context_after: Number of characters to show after each match (default: from range_size)

    Returns:
        Text string containing matches with context and character positions
    """
    # Use range_size defaults if not specified
    if context_before is None:
        context_before = abs(range_size[0])
    if context_after is None:
        context_after = range_size[1]

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        matches = list(re.finditer(pattern, content))
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")

    if not matches:
        return f"No matches found for pattern: {pattern}"

    # Limit to max_matches
    matches = matches[:max_matches]

    display_path = os.path.relpath(original_filepath if original_filepath else filepath)
    if len(matches) < max_matches:
        result_parts = [f"Found {len(matches)} match(es) (showing first {max_matches}):\n"]
    else:
        result_parts = [f"Found {len(matches)} matches:\n"]

    for i, match in enumerate(matches, 1):
        match_start = match.start()
        match_end = match.end()

        # Calculate context range
        context_start = max(0, match_start - context_before)
        context_end = min(len(content), match_end + context_after)

        # Convert to 1-indexed for display
        display_start = context_start + 1
        display_end = context_end

        # Extract context
        context = content[context_start:context_end]

        # Calculate where the match is within the context (for highlighting)
        match_offset_in_context = match_start - context_start
        match_length = match_end - match_start

        result_parts.append(f"\n--- Match {i} [Characters {display_start}-{display_end}] ---")
        result_parts.append(f"To read this section: reader {display_path} -s {display_start} {display_end}")
        result_parts.append(f"Match position: characters {match_start + 1}-{match_end}\n")

        # Show context with the match highlighted
        prefix = "..." if context_start > 0 else ""
        suffix = "..." if context_end < len(content) else ""

        # Split context to highlight the match
        before_match = context[:match_offset_in_context]
        matched_text = context[match_offset_in_context:match_offset_in_context + match_length]
        after_match = context[match_offset_in_context + match_length:]

        result_parts.append(f"{prefix}{before_match}>>>{matched_text}<<<{after_match}{suffix}")

    return '\n'.join(result_parts)
