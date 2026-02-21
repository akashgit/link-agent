/**
 * Strip markdown formatting from text for LinkedIn-clean display.
 * Mirrors backend logic in backend/app/utils/linkedin.py.
 */
export function stripMarkdown(text: string): string {
  let result = text;

  for (let pass = 0; pass < 3; pass++) {
    const prev = result;

    // 1. Code fences (remove entirely)
    result = result.replace(/```[\s\S]*?```/g, "");
    // 2. Inline code (keep inner text)
    result = result.replace(/`([^`]+)`/g, "$1");
    // 3. Bold-italic (3 stars)
    result = result.replace(/\*\*\*(.+?)\*\*\*/g, "$1");
    // 4. Bold (2 stars)
    result = result.replace(/\*\*(.+?)\*\*/g, "$1");
    // 5. Bold underscore
    result = result.replace(/__(.+?)__/g, "$1");
    // 6. Italic star
    result = result.replace(/\*(.+?)\*/g, "$1");
    // 7. Italic underscore
    result = result.replace(/(?<!\w)_(.+?)_(?!\w)/g, "$1");
    // 8. Strikethrough
    result = result.replace(/~~(.+?)~~/g, "$1");
    // 9. Headers
    result = result.replace(/^#{1,6}\s+/gm, "");
    // 10. Unordered lists
    result = result.replace(/^[-*]\s+/gm, "");
    // 11. Numbered lists
    result = result.replace(/^\d+\.\s+/gm, "");
    // 12. Links
    result = result.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");

    if (result === prev) break;
  }

  // Final cleanup: remove orphaned * and ` at word boundaries
  result = result.replace(/(?<!\S)\*{1,3}(?=\S)/g, "");
  result = result.replace(/(?<=\S)\*{1,3}(?!\S)/g, "");
  result = result.replace(/(?<!\S)`(?=\S)/g, "");
  result = result.replace(/(?<=\S)`(?!\S)/g, "");

  return result;
}
