import re

import grapheme


LINKEDIN_CHAR_LIMIT = 3000
LINKEDIN_HOOK_CUTOFF = 140
RECOMMENDED_MIN = 1300
RECOMMENDED_MAX = 2000

# Markdown patterns to strip
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_STAR_RE = re.compile(r"\*(.+?)\*")
_ITALIC_UNDER_RE = re.compile(r"(?<!\w)_(.+?)_(?!\w)")
_HEADER_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_LIST_RE = re.compile(r"^[-*]\s+", re.MULTILINE)
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")

_MARKDOWN_DETECT_RE = re.compile(
    r"\*\*.+?\*\*|(?<!\w)_.+?_(?!\w)|^#{1,6}\s+|^[-*]\s+|\[.+?\]\(.+?\)|`.+?`",
    re.MULTILINE,
)


def count_linkedin_chars(text: str) -> int:
    """Count characters using grapheme clusters for accurate emoji/compound char counting."""
    return grapheme.length(text)


def strip_markdown(text: str) -> str:
    """Remove markdown formatting, converting to plain text suitable for LinkedIn."""
    result = text
    result = _BOLD_RE.sub(r"\1", result)
    result = _ITALIC_STAR_RE.sub(r"\1", result)
    result = _ITALIC_UNDER_RE.sub(r"\1", result)
    result = _HEADER_RE.sub("", result)
    result = _LIST_RE.sub("", result)
    result = _LINK_RE.sub(r"\1", result)
    result = _INLINE_CODE_RE.sub(r"\1", result)
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
