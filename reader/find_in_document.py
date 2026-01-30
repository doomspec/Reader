import os
import re

def find_in_document(filepath: str, pattern: str, original_filepath: str | None = None, max_matches: int = 20, context_before: int = -50, context_after: int = 100) -> str:
    """
    Find regex pattern matches in the document and return context around each match.

    Args:
        filepath: Path to the document file
        pattern: Regex pattern to search for
        original_filepath: Original file path (e.g., PDF path) to display in output
        max_matches: Maximum number of matches to return (default: 20)
        context_before: Number of characters to show before each match
        context_after: Number of characters to show after each match

    Returns:
        Text string containing matches with context and character positions
    """
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
