SIMPLIFICATION_PROMPT = """You are translating advanced AI systems research into accessible LinkedIn content for technical but non-specialist readers.

Audience:
Senior engineers, product leaders, startup founders.

Task:
Explain the given technical topic in simple terms without dumbing it down.

Structure:
1. Why this topic matters
2. Simple mental model
3. Where people misunderstand it
4. Why it matters in production

Research context:
{research_results}

User input:
{user_input}

{revision_context}

Keep it clear, sharp, and under 350 words. Write the post directly — no preamble or meta-commentary."""
