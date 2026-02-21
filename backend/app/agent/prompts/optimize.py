OPTIMIZE_PROMPT = """You are a LinkedIn algorithm optimization specialist backed by research on 1.8M+ LinkedIn posts. Take the following LinkedIn post draft and optimize it for maximum reach and engagement.

Optimization rules:

HOOK (first 210 characters)
1. The first 210 characters are the mobile "see more" fold — 72% of LinkedIn users are on mobile. Lead with a bold claim, surprising statistic, or contrarian take that compels the reader to tap "see more"
2. The hook must create curiosity or tension immediately. Avoid generic openings like "I'm excited to share…"

STRUCTURE & VISUAL HIERARCHY
3. Use short paragraphs of 1-3 sentences max. Every 2-3 sentences should have a line break. Use single-sentence paragraphs for impact
4. Use Unicode bullets and symbols for scannable lists: → • ✓ ▸ — LinkedIn does NOT render markdown, so never use *, -, or # for formatting
5. Total post must be strictly under 3000 characters (LinkedIn hard limit). Ideal range is 1300-2000 characters for optimal reach

EMOJIS
6. Use 1-3 emojis max, placed strategically at section starts or key emphasis points. Never use emoji clusters (multiple emojis in a row) or purely decorative emojis. Emojis should serve as visual anchors, not decoration — research shows >5 emojis hurts credibility and triggers "AI-generated" suspicion

ENGAGEMENT
7. End with a clear question to encourage comments — posts ending with a question get 2x more comments
8. Suggest 3-5 relevant hashtags (not too niche, not too broad)

FORMAT
9. Output plain text only — no markdown formatting (no **, no _, no #, no []()). LinkedIn does not render markdown

Current draft:
{draft_content}

Post format: {post_format}
Content pillar: {content_pillar}

Return the optimized post with these sections:

## Optimized Post
(the full optimized post text)

## Changes Made
(numbered list of changes)

## Suggested Hashtags
(list of hashtags)
"""

FACT_CHECK_SECTION = """

FACT-CHECK RESULTS
The following factual claims were checked against web sources. Review them carefully and apply corrections to the optimized post:

{claims_text}

Instructions:
→ If a claim is contradicted by sources, correct it in the optimized post with accurate information
→ If a claim cannot be verified, soften the language (e.g., "reportedly", "according to some estimates")
→ If a claim is confirmed, keep it as-is

After ## Suggested Hashtags, add this section:

## Sources
(list the most relevant source URLs from the fact-check results that support claims in the post, formatted as: Source Title - URL)
"""


def build_optimize_prompt(
    draft_content: str,
    post_format: str,
    content_pillar: str,
    fact_check_results: list[dict] | None = None,
) -> str:
    """Build the full optimize prompt, conditionally including fact-check section."""
    prompt = OPTIMIZE_PROMPT.format(
        draft_content=draft_content,
        post_format=post_format,
        content_pillar=content_pillar,
    )

    if fact_check_results:
        claims_lines = []
        for i, item in enumerate(fact_check_results, 1):
            claim_block = f"Claim {i}: {item['claim']}\n"
            claim_block += f"  Search answer: {item.get('search_answer', 'No answer available')}\n"
            for src in item.get("sources", []):
                claim_block += f"  Source: {src.get('title', '')} - {src.get('url', '')}\n"
                if src.get("snippet"):
                    claim_block += f"    Snippet: {src['snippet']}\n"
            claims_lines.append(claim_block)

        prompt += FACT_CHECK_SECTION.format(claims_text="\n".join(claims_lines))

    return prompt
