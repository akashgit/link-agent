import re

import grapheme


LINKEDIN_CHAR_LIMIT = 3000
LINKEDIN_HOOK_CUTOFF = 140
RECOMMENDED_MIN = 1300
RECOMMENDED_MAX = 2000

# Markdown patterns to strip — ordered by precedence
_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_ITALIC_RE = re.compile(r"\*\*\*(.+?)\*\*\*")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_BOLD_UNDER_RE = re.compile(r"__(.+?)__")
_ITALIC_STAR_RE = re.compile(r"\*(.+?)\*")
_ITALIC_UNDER_RE = re.compile(r"(?<!\w)_(.+?)_(?!\w)")
_STRIKETHROUGH_RE = re.compile(r"~~(.+?)~~")
_HEADER_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_LIST_RE = re.compile(r"^[-*]\s+", re.MULTILINE)
_NUMBERED_LIST_RE = re.compile(r"^\d+\.\s+", re.MULTILINE)
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")

# Orphaned markers at word boundaries
_ORPHAN_STARS_RE = re.compile(r"(?<!\S)\*{1,3}(?=\S)|(?<=\S)\*{1,3}(?!\S)")
_ORPHAN_BACKTICKS_RE = re.compile(r"(?<!\S)`(?=\S)|(?<=\S)`(?!\S)")

_MARKDOWN_DETECT_RE = re.compile(
    r"\*\*\*(.+?)\*\*\*"
    r"|\*\*(.+?)\*\*"
    r"|__(.+?)__"
    r"|(?<!\w)_(.+?)_(?!\w)"
    r"|~~(.+?)~~"
    r"|^#{1,6}\s+"
    r"|^[-*]\s+"
    r"|^\d+\.\s+"
    r"|\[.+?\]\(.+?\)"
    r"|`.+?`"
    r"|```[\s\S]*?```",
    re.MULTILINE,
)


def count_linkedin_chars(text: str) -> int:
    """Count characters using grapheme clusters for accurate emoji/compound char counting."""
    return grapheme.length(text)


def strip_markdown(text: str) -> str:
    """Remove markdown formatting, converting to plain text suitable for LinkedIn.

    Processes patterns in correct precedence order and loops up to 3 passes
    to handle nested patterns.
    """
    result = text

    for _ in range(3):
        prev = result
        # 1. Code fences (remove entirely — content inside is raw)
        result = _CODE_FENCE_RE.sub("", result)
        # 2. Inline code (keep inner text)
        result = _INLINE_CODE_RE.sub(r"\1", result)
        # 3. Bold-italic (3 stars)
        result = _BOLD_ITALIC_RE.sub(r"\1", result)
        # 4. Bold (2 stars)
        result = _BOLD_RE.sub(r"\1", result)
        # 5. Bold underscore
        result = _BOLD_UNDER_RE.sub(r"\1", result)
        # 6. Italic star
        result = _ITALIC_STAR_RE.sub(r"\1", result)
        # 7. Italic underscore
        result = _ITALIC_UNDER_RE.sub(r"\1", result)
        # 8. Strikethrough
        result = _STRIKETHROUGH_RE.sub(r"\1", result)
        # 9. Headers
        result = _HEADER_RE.sub("", result)
        # 10. Unordered lists
        result = _LIST_RE.sub("", result)
        # 11. Numbered lists
        result = _NUMBERED_LIST_RE.sub("", result)
        # 12. Links
        result = _LINK_RE.sub(r"\1", result)

        if result == prev:
            break

    # Final cleanup: remove orphaned * and ` at word boundaries
    result = _ORPHAN_STARS_RE.sub("", result)
    result = _ORPHAN_BACKTICKS_RE.sub("", result)

    return result


def estimate_see_more_cutoff(text: str) -> str:
    """Return the text visible before LinkedIn's 'see more' fold."""
    first_newline = text.find("\n")
    if first_newline == -1:
        preview = text[:LINKEDIN_HOOK_CUTOFF]
    else:
        preview = text[:min(first_newline, LINKEDIN_HOOK_CUTOFF)]
    return preview


def validate_linkedin_post(text: str) -> dict:
    """Validate text against LinkedIn formatting constraints.

    Returns a dict with validation results and warnings.
    """
    char_count = count_linkedin_chars(text)
    word_count = len(text.split())
    hook_preview = estimate_see_more_cutoff(text)
    warnings: list[str] = []

    if char_count > LINKEDIN_CHAR_LIMIT:
        warnings.append(
            f"Post exceeds LinkedIn's {LINKEDIN_CHAR_LIMIT} character limit "
            f"({char_count} characters)"
        )

    hook_len = count_linkedin_chars(hook_preview)
    if hook_len > LINKEDIN_HOOK_CUTOFF:
        warnings.append(
            f"Hook is {hook_len} characters — may be cut off before 'see more' "
            f"(recommended: under {LINKEDIN_HOOK_CUTOFF})"
        )

    if _MARKDOWN_DETECT_RE.search(text):
        warnings.append(
            "Markdown formatting detected — LinkedIn renders plain text only"
        )

    if char_count < RECOMMENDED_MIN:
        warnings.append(
            f"Post is short ({char_count} chars) — "
            f"recommended range is {RECOMMENDED_MIN}-{RECOMMENDED_MAX} characters"
        )
    elif char_count > RECOMMENDED_MAX and char_count <= LINKEDIN_CHAR_LIMIT:
        warnings.append(
            f"Post is {char_count} characters — "
            f"optimal engagement range is {RECOMMENDED_MIN}-{RECOMMENDED_MAX}"
        )

    return {
        "valid": char_count <= LINKEDIN_CHAR_LIMIT and not _MARKDOWN_DETECT_RE.search(text),
        "char_count": char_count,
        "word_count": word_count,
        "hook_preview": hook_preview,
        "warnings": warnings,
    }
