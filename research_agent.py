import os
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List


# ── State ─────────────────────────────────────────────────────
class ResearchState(TypedDict):
    topic: str
    search_results: List[str]
    synthesized_research: str
    final_report: str
    error: Optional[str]

# ── LLM ───────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Node 1: Scrape web results ────────────────────────────────
def scrape_research(state: ResearchState) -> ResearchState:
    print(f"🌐 Searching the web for: {state['topic']}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    collected = []
    
    # Search using DuckDuckGo (no API key needed)
    search_url = f"https://html.duckduckgo.com/html/?q={state['topic'].replace(' ', '+')}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract result snippets
        results = soup.find_all("a", class_="result__snippet")
        for r in results[:8]:
            text = r.get_text(strip=True)
            if text and len(text) > 40:
                collected.append(text)
        
        if not collected:
            # Fallback: extract any paragraph text
            paragraphs = soup.find_all("p")
            for p in paragraphs[:10]:
                text = p.get_text(strip=True)
                if len(text) > 60:
                    collected.append(text)
        
        print(f"   ✓ Found {len(collected)} research snippets")
        return {**state, "search_results": collected, "error": None}
    
    except Exception as e:
        return {**state, "error": str(e), "search_results": []}

# ── Node 2: Synthesize research ───────────────────────────────
def synthesize_research(state: ResearchState) -> ResearchState:
    if state.get("error") or not state["search_results"]:
        # If scraping failed, use LLM's own knowledge
        print("   ⚠ Using AI knowledge base instead of web results...")
        return {**state, 
                "synthesized_research": f"Research topic: {state['topic']}. Using internal knowledge.",
                "error": None}
    
    print("🧠 Synthesizing research...")
    
    raw_text = "\n\n".join([f"- {r}" for r in state["search_results"]])
    
    prompt = f"""
You are a research analyst. Based on these web snippets about "{state['topic']}", 
extract and organize the key facts, trends, and important points.

Web snippets:
{raw_text}

Provide:
1. Main facts (5-7 bullet points)
2. Current trends
3. Key players or examples
4. Any controversies or challenges

Be factual and organized.
    """
    
    response = llm.invoke(prompt)
    return {**state, "synthesized_research": response.content}

# ── Node 3: Write final report ────────────────────────────────
def write_research_report(state: ResearchState) -> ResearchState:
    print("📝 Writing research report...")
    
    prompt = f"""
You are a professional research writer. Write a comprehensive research report on:
"{state['topic']}"

Using this synthesized research:
{state['synthesized_research']}

Structure the report as:
1. OVERVIEW (what this topic is, why it matters)
2. KEY FINDINGS (5 specific, numbered points with details)  
3. CURRENT TRENDS (what's happening right now)
4. OPPORTUNITIES & CHALLENGES
5. CONCLUSION & OUTLOOK

Write in a professional tone. Be specific. Minimum 500 words.
    """
    
    response = llm.invoke(prompt)
    return {**state, "final_report": response.content}

# ── Error handler ─────────────────────────────────────────────
def handle_error(state: ResearchState) -> ResearchState:
    print(f"❌ Error: {state['error']}")
    return {**state, "final_report": f"Research error: {state['error']}"}

# ── Router ────────────────────────────────────────────────────
def route_after_scrape(state: ResearchState) -> str:
    # Even if scraping fails we continue — LLM uses own knowledge
    return "synthesize"

# ── Build Graph ───────────────────────────────────────────────
def build_research_agent():
    graph = StateGraph(ResearchState)
    
    graph.add_node("scrape_research", scrape_research)
    graph.add_node("synthesize_research", synthesize_research)
    graph.add_node("write_research_report", write_research_report)
    graph.add_node("handle_error", handle_error)
    
    graph.set_entry_point("scrape_research")
    
    graph.add_conditional_edges(
        "scrape_research",
        route_after_scrape,
        {"synthesize": "synthesize_research"}
    )
    
    graph.add_edge("synthesize_research", "write_research_report")
    graph.add_edge("write_research_report", END)
    graph.add_edge("handle_error", END)
    
    return graph.compile()

# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("   AI RESEARCH AGENT")
    print("=" * 50)
    
    topic = input("\nEnter research topic: ").strip()
    
    agent = build_research_agent()
    
    result = agent.invoke({
        "topic": topic,
        "search_results": [],
        "synthesized_research": "",
        "final_report": "",
        "error": None
    })
    
    print("\n" + "=" * 50)
    print("   RESEARCH REPORT")
    print("=" * 50)
    print(result["final_report"])
    
    # Save report
    filename = f"research_{topic[:30].replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result["final_report"])
    print(f"\n✅ Report saved to {filename}")