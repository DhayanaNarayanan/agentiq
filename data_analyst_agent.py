from dotenv import load_dotenv
import os
import pandas as pd
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

load_dotenv()

# ── State: what flows between agents ──────────────────────────
class AnalystState(TypedDict):
    file_path: str
    raw_summary: str
    insights: str
    final_report: str
    error: Optional[str]

# ── LLM ───────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Node 1: Read & summarize the CSV ──────────────────────────
def read_data(state: AnalystState) -> AnalystState:
    print("📂 Reading your data file...")
    try:
        df = pd.read_csv(state["file_path"])
        
        summary = f"""
DATASET OVERVIEW:
- Rows: {df.shape[0]}
- Columns: {df.shape[1]}
- Column names: {list(df.columns)}
- Data types: {df.dtypes.to_dict()}
- Missing values: {df.isnull().sum().to_dict()}

SAMPLE DATA (first 5 rows):
{df.head().to_string()}

BASIC STATISTICS:
{df.describe().to_string()}
        """
        return {**state, "raw_summary": summary, "error": None}
    
    except Exception as e:
        return {**state, "error": str(e)}

# ── Node 2: Generate insights ─────────────────────────────────
def generate_insights(state: AnalystState) -> AnalystState:
    if state.get("error"):
        return state
    
    print("🧠 Analyzing patterns and generating insights...")
    
    prompt = f"""
You are an expert data analyst. Analyze this dataset summary and provide:

1. KEY FINDINGS — What are the 5 most important things you notice?
2. PATTERNS — Any trends, correlations, or anomalies?
3. DATA QUALITY — Any issues with missing values or data types?
4. BUSINESS QUESTIONS — What 3 questions should someone ask about this data?

Dataset Summary:
{state["raw_summary"]}

Be specific, use numbers from the data, and be concise.
    """
    
    response = llm.invoke(prompt)
    return {**state, "insights": response.content}

# ── Node 3: Write the final report ────────────────────────────
def write_report(state: AnalystState) -> AnalystState:
    if state.get("error"):
        return state
    
    print("📝 Writing your final report...")
    
    prompt = f"""
You are a professional data analyst writing a report for a business client.

Using these insights, write a clean, professional DATA ANALYSIS REPORT with:
- Executive Summary (2-3 sentences)
- Key Findings (numbered list with specific numbers)
- Recommendations (3 actionable next steps)
- Conclusion

Keep it clear, professional, and under 400 words.

Insights to use:
{state["insights"]}
    """
    
    response = llm.invoke(prompt)
    return {**state, "final_report": response.content}

# ── Error handler ─────────────────────────────────────────────
def handle_error(state: AnalystState) -> AnalystState:
    print(f"❌ Error: {state['error']}")
    return {**state, "final_report": f"Error processing file: {state['error']}"}

# ── Router: go to error handler if something broke ────────────
def route_after_read(state: AnalystState) -> str:
    if state.get("error"):
        return "error"
    return "insights"

# ── Build the Graph ───────────────────────────────────────────
def build_analyst_agent():
    graph = StateGraph(AnalystState)
    
    graph.add_node("read_data", read_data)
    graph.add_node("generate_insights", generate_insights)
    graph.add_node("write_report", write_report)
    graph.add_node("handle_error", handle_error)
    
    graph.set_entry_point("read_data")
    
    graph.add_conditional_edges(
        "read_data",
        route_after_read,
        {"insights": "generate_insights", "error": "handle_error"}
    )
    
    graph.add_edge("generate_insights", "write_report")
    graph.add_edge("write_report", END)
    graph.add_edge("handle_error", END)
    
    return graph.compile()

# ── Run it ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("   AI DATA ANALYST AGENT")
    print("=" * 50)
    
    file = input("\nEnter the path to your CSV file: ").strip()
    
    agent = build_analyst_agent()
    
    result = agent.invoke({
        "file_path": file,
        "raw_summary": "",
        "insights": "",
        "final_report": "",
        "error": None
    })
    
    print("\n" + "=" * 50)
    print("   FINAL REPORT")
    print("=" * 50)
    print(result["final_report"])
    
    # Save report to file
    with open("analysis_report.txt", "w") as f:
        f.write(result["final_report"])
    print("\n✅ Report saved to analysis_report.txt")