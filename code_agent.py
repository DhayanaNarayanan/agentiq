import os
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import subprocess
import tempfile


# ── State ─────────────────────────────────────────────────────
class CodeState(TypedDict):
    problem: str
    generated_code: str
    explanation: str
    test_result: str
    final_output: str
    error: Optional[str]

# ── LLM ───────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Node 1: Generate Code ─────────────────────────────────────
def generate_code(state: CodeState) -> CodeState:
    print("💻 Generating code...")

    prompt = f"""
You are an expert Python developer. Write clean, working Python code for this task:

TASK: {state['problem']}

Rules:
- Write ONLY the Python code, no explanation
- Add clear comments inside the code
- Make it beginner-friendly and readable
- Include a main() function
- Print the output so results are visible
- Use only standard library or common packages (pandas, numpy, requests)

Return ONLY the code block, nothing else.
    """

    response = llm.invoke(prompt)
    code = response.content

    # Clean markdown code fences if present
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()

    return {**state, "generated_code": code, "error": None}

# ── Node 2: Test the Code ─────────────────────────────────────
def test_code(state: CodeState) -> CodeState:
    if state.get("error"):
        return state

    print("🧪 Testing the code...")

    try:
        # Write code to a temp file and run it safely
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        ) as f:
            f.write(state["generated_code"])
            temp_path = f.name

        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=15  # 15 second limit
        )

        if result.returncode == 0:
            output = result.stdout or "Code ran successfully with no printed output."
            print(f"   ✓ Code executed successfully")
        else:
            output = f"Error during execution:\n{result.stderr}"
            print(f"   ⚠ Code had errors — will fix")

        os.unlink(temp_path)  # Clean up temp file
        return {**state, "test_result": output}

    except subprocess.TimeoutExpired:
        return {**state, "test_result": "Code timed out after 15 seconds."}
    except Exception as e:
        return {**state, "test_result": f"Could not run code: {str(e)}"}

# ── Node 3: Explain the Code ──────────────────────────────────
def explain_code(state: CodeState) -> CodeState:
    if state.get("error"):
        return state

    print("📖 Writing explanation...")

    prompt = f"""
You are a coding teacher. Explain this Python code clearly to a beginner:

CODE:
{state['generated_code']}

TEST OUTPUT:
{state['test_result']}

Write:
1. WHAT IT DOES (1 sentence summary)
2. HOW IT WORKS (step by step, simple language)
3. KEY CONCEPTS USED (what Python concepts this teaches)
4. HOW TO MODIFY IT (2 ways to extend or change it)

Keep it friendly, clear, and educational.
    """

    response = llm.invoke(prompt)
    return {**state, "explanation": response.content}

# ── Node 4: Package Final Output ─────────────────────────────
def package_output(state: CodeState) -> CodeState:
    final = f"""
{'='*55}
GENERATED CODE
{'='*55}
{state['generated_code']}

{'='*55}
TEST OUTPUT
{'='*55}
{state['test_result']}

{'='*55}
EXPLANATION
{'='*55}
{state['explanation']}
    """
    return {**state, "final_output": final}

# ── Build Graph ───────────────────────────────────────────────
def build_code_agent():
    graph = StateGraph(CodeState)

    graph.add_node("generate_code", generate_code)
    graph.add_node("test_code", test_code)
    graph.add_node("explain_code", explain_code)
    graph.add_node("package_output", package_output)

    graph.set_entry_point("generate_code")
    graph.add_edge("generate_code", "test_code")
    graph.add_edge("test_code", "explain_code")
    graph.add_edge("explain_code", "package_output")
    graph.add_edge("package_output", END)

    return graph.compile()

# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("   AI CODE GENERATOR AGENT")
    print("=" * 55)

    print("\nExamples you can try:")
    print("  - Create a sales data analyzer with sample data")
    print("  - Build a word frequency counter from text")
    print("  - Write a CSV file merger for two datasets")
    print("  - Create a simple linear regression from scratch")

    problem = input("\nDescribe what you want to code: ").strip()

    agent = build_code_agent()

    result = agent.invoke({
        "problem": problem,
        "generated_code": "",
        "explanation": "",
        "test_result": "",
        "final_output": "",
        "error": None
    })

    print(result["final_output"])

    # Save output
    filename = f"code_{problem[:25].replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result["final_output"])
    print(f"\n✅ Saved to {filename}")