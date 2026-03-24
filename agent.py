"""Client Meeting Brief — Multi-Agent System.

Orchestrator coordinates two specialist agents:
  1. Research Agent  – uses Tavily to find recent news/articles about a company
  2. Writer Agent    – synthesises raw research into a polished 3-paragraph briefing
"""

import os
import sys

from dotenv import load_dotenv
from strands import Agent, tool
from tavily import TavilyClient

load_dotenv()

# ── Tavily search tool ──────────────────────────────────────────────────────

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


@tool
def search_company_news(query: str) -> str:
    """Search the web for recent news and articles about a company.

    Args:
        query: The search query, e.g. 'Acme Corp recent product launches'.
    """
    results = tavily.search(query=query, max_results=5, search_depth="advanced")
    summaries = []
    for r in results.get("results", []):
        summaries.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}\n")
    return "\n---\n".join(summaries) if summaries else "No results found."


# ── Specialist agents ────────────────────────────────────────────────────────

research_agent = Agent(
    tools=[search_company_news],
    system_prompt=(
        "You are a research specialist. Given a company name and optional focus area, "
        "use the search_company_news tool to find 3-5 recent and relevant articles, "
        "press releases, or blog posts. Return a structured summary of your findings "
        "with key facts, dates, and sources. Do NOT fabricate information."
    ),
    callback_handler=None,  # suppress streaming output for sub-agents
)

writer_agent = Agent(
    system_prompt=(
        "You are a professional business writer. You receive raw research notes about "
        "a company and produce a concise, well-structured client meeting briefing. "
        "The briefing MUST be exactly 3 paragraphs:\n"
        "  1. Company overview and recent strategic direction\n"
        "  2. Key recent developments, product launches, or news\n"
        "  3. Talking points and conversation starters for the meeting\n"
        "Write in a confident, professional tone. Cite sources where possible."
    ),
    callback_handler=None,
)


# ── Orchestrator ─────────────────────────────────────────────────────────────

@tool
def research(company: str, focus: str = "") -> str:
    """Run the research agent to gather recent information about a company.

    Args:
        company: The company name to research.
        focus: Optional focus area like a product, department, or topic.
    """
    query = f"{company} recent news announcements"
    if focus:
        query += f" {focus}"
    result = research_agent(f"Research this company: {company}. Search query: {query}")
    return str(result)


@tool
def write_brief(research_notes: str) -> str:
    """Send raw research notes to the writer agent to produce a polished briefing.

    Args:
        research_notes: The raw research findings to synthesise into a brief.
    """
    result = writer_agent(
        f"Write a 3-paragraph client meeting briefing from these research notes:\n\n{research_notes}"
    )
    return str(result)


orchestrator = Agent(
    tools=[research, write_brief],
    system_prompt=(
        "You are a client meeting brief coordinator. When given a company name "
        "(and optional focus area), you:\n"
        "  1. Call the 'research' tool to gather recent news and information\n"
        "  2. Pass the research results to the 'write_brief' tool\n"
        "  3. Return the final briefing to the user\n"
        "Always execute both steps. Do not skip the research step."
    ),
)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python agent.py <company> [focus area]")
        print('Example: uv run python agent.py "Anthropic" "Claude model releases"')
        sys.exit(1)

    company = sys.argv[1]
    focus = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    prompt = f"Prepare a client meeting brief for {company}."
    if focus:
        prompt += f" Focus on: {focus}."

    print(f"\n🔍 Preparing brief for: {company}")
    if focus:
        print(f"📌 Focus: {focus}")
    print("─" * 50)

    response = orchestrator(prompt)
    print("\n" + str(response))
