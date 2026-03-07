from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from data_analyst_agent import build_analyst_agent
from research_agent import build_research_agent
from code_agent import build_code_agent

load_dotenv()

# ── State ─────────────────────────────────────────────────────
class OrchestratorState(TypedDict):
    user_task: str
    route: str
    file_path: Optional[str]
    final_output: str
    error: Optional[str]

# ── LLM ───────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Node 1: Understand & Route the Task ───────────────────────
def understand_task(state: OrchestratorState) -> OrchestratorState:
    print("\n🤔 Understanding your task...")

    prompt = f"""
You are a task router for an AI agent platform.
Analyze this user task and decide which agent should handle it.

USER TASK: {state['user_task']}

Rules:
- Reply with ONLY one word: DATA, RESEARCH, or CODE
- DATA → if task involves analyzing a CSV, spreadsheet, or dataset file
- RESEARCH → if task involves researching a topic, summarizing information, or writing a report about something
- CODE → if task involves writing, generating, fixing, or explaining code

Reply with only: DATA, RESEARCH, or CODE
    """

    response = llm.invoke(prompt)
    route = response.content.strip().upper()

    # Safety check
    if route not in ["DATA", "RESEARCH", "CODE"]:
        route = "RESEARCH"  # default fallback

    route_names = {
        "DATA": "📊 Data Analyst Agent",
        "RESEARCH": "🌐 Research & Writer Agent",
        "CODE": "💻 Code Generator Agent"
    }

    print(f"   ✓ Routing to: {route_names[route]}")
    return {**state, "route": route}

# ── Node 2: Run the right agent ───────────────────────────────
def run_agent(state: OrchestratorState) -> OrchestratorState:
    route = state["route"]

    try:
        if route == "DATA":
            if not state.get("file_path"):
                return {**state, 
                        "final_output": "❌ This task needs a CSV file. Please provide a file path.",
                        "error": "No file path provided"}

            agent = build_analyst_agent()
            result = agent.invoke({
                "file_path": state["file_path"],
                "raw_summary": "",
                "insights": "",
                "final_report": "",
                "error": None
            })
            return {**state, "final_output": result["final_report"]}

        elif route == "RESEARCH":
            agent = build_research_agent()
            result = agent.invoke({
                "topic": state["user_task"],
                "search_results": [],
                "synthesized_research": "",
                "final_report": "",
                "error": None
            })
            return {**state, "final_output": result["final_report"]}

        elif route == "CODE":
            agent = build_code_agent()
            result = agent.invoke({
                "problem": state["user_task"],
                "generated_code": "",
                "explanation": "",
                "test_result": "",
                "final_output": "",
                "error": None
            })
            return {**state, "final_output": result["final_output"]}

    except Exception as e:
        return {**state, "final_output": f"Agent error: {str(e)}", "error": str(e)}

# ── Node 3: Format & Save Output ─────────────────────────────
def format_output(state: OrchestratorState) -> OrchestratorState:
    route_labels = {
        "DATA": "DATA ANALYSIS REPORT",
        "RESEARCH": "RESEARCH REPORT",
        "CODE": "GENERATED CODE & EXPLANATION"
    }

    label = route_labels.get(state["route"], "OUTPUT")

    final = f"""
{'='*55}
TASK: {state['user_task']}
HANDLED BY: {state['route']} AGENT
{'='*55}

{state['final_output']}
    """

    # Save to file
    filename = f"output_{state['route'].lower()}_{state['user_task'][:20].replace(' ','_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final)

    print(f"\n✅ Output saved to {filename}")
    return {**state, "final_output": final}

# ── Build Orchestrator Graph ──────────────────────────────────
def build_orchestrator():
    graph = StateGraph(OrchestratorState)

    graph.add_node("understand_task", understand_task)
    graph.add_node("run_agent", run_agent)
    graph.add_node("format_output", format_output)

    graph.set_entry_point("understand_task")
    graph.add_edge("understand_task", "run_agent")
    graph.add_edge("run_agent", "format_output")
    graph.add_edge("format_output", END)

    return graph.compile()

# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("   🧠 AI AGENT ORCHESTRATOR")
    print("   Your intelligent multi-agent platform")
    print("=" * 55)

    print("\nWhat can I help you with?")
    print("  Examples:")
    print("  - 'Research the future of renewable energy'")
    print("  - 'Write code to scrape a website'")
    print("  - 'Analyze my sales data' (needs CSV file)")

    task = input("\n📝 Your task: ").strip()

    # Ask for file only if needed
    file_path = None
    if any(word in task.lower() for word in ["analyze", "csv", "data", "dataset", "file"]):
        file_path = input("📂 CSV file path (press Enter to skip): ").strip() or None

    orchestrator = build_orchestrator()

    result = orchestrator.invoke({
        "user_task": task,
        "route": "",
        "file_path": file_path,
        "final_output": "",
        "error": None
    })

    print(result["final_output"])