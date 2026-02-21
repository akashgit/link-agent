"""Seed the content calendar with the 30-day roadmap from LinkedIn Analysis."""
import asyncio
from datetime import date

from sqlalchemy import select
from app.db.session import async_session
from app.models.calendar_entry import CalendarEntry, CalendarStatus
from app.models.post import ContentPillar, PostFormat

ROADMAP = [
    # Week 1
    {
        "scheduled_date": date(2026, 2, 19),
        "content_pillar": ContentPillar.ENTERPRISE_REALITY,
        "post_format": PostFormat.STRONG_POV,
        "topic": "Benchmarks misrepresent enterprise reality - challenge one-shot success benchmarks",
    },
    {
        "scheduled_date": date(2026, 2, 21),
        "content_pillar": ContentPillar.INFERENCE_SCALING,
        "post_format": PostFormat.SIMPLIFICATION,
        "topic": "Pass^k reliability explained - demystify multi-run reliability metrics",
    },
    {
        "scheduled_date": date(2026, 2, 24),
        "content_pillar": ContentPillar.AGENTOPS,
        "post_format": PostFormat.FRAMEWORK,
        "topic": "3 layers of agent reliability - define planning, execution and evaluation layers",
    },
    {
        "scheduled_date": date(2026, 2, 26),
        "content_pillar": ContentPillar.ENTERPRISE_REALITY,
        "post_format": PostFormat.LEADER_LENS,
        "topic": "What enterprise buyers misunderstand about AI agents - lessons from the field",
    },
    # Week 2
    {
        "scheduled_date": date(2026, 3, 2),
        "content_pillar": ContentPillar.AGENTOPS,
        "post_format": PostFormat.STRONG_POV,
        "topic": "Single-agent vs multi-agent systems - why teams of sub-agents are inevitable",
    },
    {
        "scheduled_date": date(2026, 3, 4),
        "content_pillar": ContentPillar.INFERENCE_SCALING,
        "post_format": PostFormat.SIMPLIFICATION,
        "topic": "Inference-time scaling - explain latency vs throughput trade-offs",
    },
    {
        "scheduled_date": date(2026, 3, 5),
        "content_pillar": ContentPillar.AGENTOPS,
        "post_format": PostFormat.FRAMEWORK,
        "topic": "Agent maturity model - levels from scripts to agents to autonomous teams",
    },
    {
        "scheduled_date": date(2026, 3, 6),
        "content_pillar": ContentPillar.LEADERSHIP,
        "post_format": PostFormat.STORY,
        "topic": "Inside InstructLab - expand on the 3 AM lobby story with a lesson about resilience",
    },
    # Week 3
    {
        "scheduled_date": date(2026, 3, 9),
        "content_pillar": ContentPillar.LEADERSHIP,
        "post_format": PostFormat.LEADER_LENS,
        "topic": "Hiring for AgentOps - traits to look for in agent engineers",
    },
    {
        "scheduled_date": date(2026, 3, 11),
        "content_pillar": ContentPillar.ENTERPRISE_REALITY,
        "post_format": PostFormat.SIMPLIFICATION,
        "topic": "OfficeQA and tau-bench - break down why these benchmarks matter",
    },
    {
        "scheduled_date": date(2026, 3, 12),
        "content_pillar": ContentPillar.AGENTOPS,
        "post_format": PostFormat.STRONG_POV,
        "topic": "Why prompt engineering won't scale - systems-level critique",
    },
    {
        "scheduled_date": date(2026, 3, 13),
        "content_pillar": ContentPillar.ENTERPRISE_REALITY,
        "post_format": PostFormat.FRAMEWORK,
        "topic": "4 pillars of enterprise agent deployment - security, auditability, domain specificity, recovery",
    },
    # Week 4
    {
        "scheduled_date": date(2026, 3, 16),
        "content_pillar": ContentPillar.RESEARCH_TO_PRODUCT,
        "post_format": PostFormat.STORY,
        "topic": "When an agent failed in production - anonymised failure + fix; lesson about evaluation loops",
    },
    {
        "scheduled_date": date(2026, 3, 18),
        "content_pillar": ContentPillar.LEADERSHIP,
        "post_format": PostFormat.LEADER_LENS,
        "topic": "Evaluating agent engineers - suggest rubrics for interviews",
    },
    {
        "scheduled_date": date(2026, 3, 19),
        "content_pillar": ContentPillar.AGENTOPS,
        "post_format": PostFormat.SIMPLIFICATION,
        "topic": "Multi-agent coordination - simple mental model (planner, executor, critic)",
    },
    {
        "scheduled_date": date(2026, 3, 20),
        "content_pillar": ContentPillar.AGENTOPS,
        "post_format": PostFormat.FRAMEWORK,
        "topic": "Stateful vs stateless agents - pros/cons and when to use each",
    },
]


async def seed():
    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(CalendarEntry).limit(1))
        if result.scalar_one_or_none():
            print("Calendar already seeded, skipping.")
            return

        for entry_data in ROADMAP:
            entry = CalendarEntry(
                scheduled_date=entry_data["scheduled_date"],
                content_pillar=entry_data["content_pillar"],
                post_format=entry_data["post_format"],
                topic=entry_data["topic"],
                status=CalendarStatus.PLANNED,
            )
            session.add(entry)

        await session.commit()
        print(f"Seeded {len(ROADMAP)} calendar entries.")


if __name__ == "__main__":
    asyncio.run(seed())
