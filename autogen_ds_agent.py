import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# ── LLM Setup ─────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY")
)

# ── Helper: run code safely ───────────────────────────────────
import subprocess
import tempfile

def run_code(code: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        ) as f:
            f.write(code)
            path = f.name
        result = subprocess.run(
            ["python", path],
            capture_output=True, text=True, timeout=120
        )
        os.unlink(path)
        if result.returncode == 0:
            return result.stdout or "Code ran successfully."
        else:
            return f"ERROR:\n{result.stderr}"
    except Exception as e:
        return f"Failed to run: {str(e)}"

# ══════════════════════════════════════════════════════════════
# AGENT 1 — EXPLORER
# Reads the CSV and understands the data deeply
# ══════════════════════════════════════════════════════════════
def explorer_agent(file_path: str) -> dict:
    print("\n" + "="*55)
    print("🔍 EXPLORER AGENT — Reading and understanding data...")
    print("="*55)

    try:
        df = pd.read_csv(file_path)

        # Deep data profile
        profile = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing": df.isnull().sum().to_dict(),
            "missing_pct": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            "numeric_cols": list(df.select_dtypes(include=np.number).columns),
            "categorical_cols": list(df.select_dtypes(include='object').columns),
            "sample": df.head(3).to_string(),
            "stats": df.describe().to_string(),
            "unique_counts": {col: df[col].nunique() for col in df.columns}
        }

        # Identify likely target column
        target_hints = ['target', 'label', 'class', 'output', 'result',
                       'price', 'salary', 'churn', 'fraud', 'status', 'survived']
        likely_target = None
        for col in df.columns:
            if col.lower() in target_hints:
                likely_target = col
                break
        if not likely_target:
            likely_target = df.columns[-1]  # default: last column

        profile["likely_target"] = likely_target
        profile["target_type"] = "classification" if df[likely_target].nunique() < 10 else "regression"

        print(f"   ✓ Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"   ✓ Target column: '{likely_target}' ({profile['target_type']})")
        print(f"   ✓ Numeric features: {len(profile['numeric_cols'])}")
        print(f"   ✓ Categorical features: {len(profile['categorical_cols'])}")
        print(f"   ✓ Missing values: {sum(v > 0 for v in profile['missing'].values())} columns affected")

        return {"status": "success", "profile": profile, "dataframe": df}

    except Exception as e:
        return {"status": "error", "error": str(e)}


# ══════════════════════════════════════════════════════════════
# AGENT 2 — STRATEGY AGENT
# Decides which ML approach to take
# ══════════════════════════════════════════════════════════════
def strategy_agent(profile: dict) -> dict:
    print("\n" + "="*55)
    print("🧠 STRATEGY AGENT — Planning ML approach...")
    print("="*55)

    prompt = f"""
You are a senior ML engineer. Analyze this dataset and create a precise ML strategy.

DATASET PROFILE:
- Shape: {profile['shape']}
- Target column: '{profile['likely_target']}'
- Task type: {profile['target_type']}
- Numeric columns: {profile['numeric_cols']}
- Categorical columns: {profile['categorical_cols']}
- Missing values: {profile['missing_pct']}
- Unique counts per column: {profile['unique_counts']}
- Sample data:
{profile['sample']}

Provide a concise ML strategy with:
1. PROBLEM TYPE: (classification/regression and why)
2. DATA CLEANING STEPS: (exactly what to do for this data)
3. FEATURE ENGINEERING: (specific steps for these columns)
4. RECOMMENDED MODELS: (top 3 models to try, with reasons)
5. PRIMARY MODEL: (single best model to start with and why)
6. EVALUATION METRIC: (best metric for this problem)
7. EXPECTED CHALLENGES: (specific issues with this dataset)

Be specific to THIS dataset. Use actual column names.
    """

    response = llm.invoke(prompt)
    strategy = response.content

    print("   ✓ ML strategy generated")
    print(f"   ✓ Task: {profile['target_type']}")
    print(f"   ✓ Strategy ready for Builder Agent")

    return {"status": "success", "strategy": strategy, "task_type": profile['target_type']}


# ══════════════════════════════════════════════════════════════
# AGENT 3 — BUILDER AGENT
# Writes and runs the actual ML code
# ══════════════════════════════════════════════════════════════
def builder_agent(file_path: str, profile: dict, strategy: str) -> dict:
    print("\n" + "="*55)
    print("⚙️  BUILDER AGENT — Writing and running ML code...")
    print("="*55)

    prompt = f"""
You are an expert ML engineer. Write complete, working Python code for this ML task.

FILE PATH: {file_path}
TARGET COLUMN: {profile['likely_target']}
TASK TYPE: {profile['target_type']}
NUMERIC COLUMNS: {profile['numeric_cols']}
CATEGORICAL COLUMNS: {profile['categorical_cols']}
MISSING VALUES: {profile['missing']}

ML STRATEGY:
{strategy}

Write COMPLETE Python code that:
1. Loads the CSV from '{file_path}' — use df = pd.read_csv('{file_path}').sample(n=10000, random_state=42) to load only 10,000 rows for speed
2. Cleans data (handle missing values, encode categoricals)
3. Splits into train/test (80/20)
4. Trains the recommended model
5. Prints evaluation metrics (accuracy/R2, classification report if classification)
6. Prints feature importances if available
7. Prints "MODEL_SCORE: X.XX" where X.XX is the main metric score

IMPORTANT RULES:
- Use only: pandas, numpy, sklearn (already installed)
- Handle ALL possible errors with try/except
- Print clear labels for every output
- Code must run completely without user input
- Only use columns that exist in the data
- Return ONLY the Python code, no explanation
```python
# Your complete ML code here
```
    """

    response = llm.invoke(prompt)
    code = response.content

    # Clean code fences
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()

    print("   ✓ ML code generated")
    print("   ⚡ Running the code now...")

    # Run the code
    result = run_code(code)

    # Extract model score
    score = "N/A"
    for line in result.split('\n'):
        if 'MODEL_SCORE:' in line:
            try:
                score = line.split('MODEL_SCORE:')[1].strip()
            except:
                pass

    print(f"   ✓ Code execution complete")
    print(f"   ✓ Model score: {score}")

    return {
        "status": "success",
        "code": code,
        "execution_result": result,
        "model_score": score
    }


# ══════════════════════════════════════════════════════════════
# AGENT 4 — VALIDATOR AGENT
# Reviews results and catches issues
# ══════════════════════════════════════════════════════════════
def validator_agent(code: str, execution_result: str, profile: dict) -> dict:
    print("\n" + "="*55)
    print("✅ VALIDATOR AGENT — Reviewing results...")
    print("="*55)

    prompt = f"""
You are a senior data scientist reviewing ML results.

DATASET: {profile['shape'][0]} rows, {profile['shape'][1]} columns
TARGET: {profile['likely_target']} ({profile['target_type']})

CODE EXECUTED:
{code[:1500]}

EXECUTION OUTPUT:
{execution_result[:1500]}

Provide a VALIDATION REPORT:
1. CODE QUALITY: (is the code correct and complete?)
2. RESULTS INTERPRETATION: (what do the metrics actually mean?)
3. MODEL PERFORMANCE: (is this good/average/poor for this type of problem?)
4. RED FLAGS: (any issues, data leakage, overfitting concerns?)
5. IMPROVEMENT SUGGESTIONS: (top 3 specific ways to improve this model)
6. PRODUCTION READINESS: (is this ready for real use?)

Be direct and specific. Use actual numbers from the output.
    """

    response = llm.invoke(prompt)
    validation = response.content

    print("   ✓ Validation complete")

    return {"status": "success", "validation": validation}


# ══════════════════════════════════════════════════════════════
# AGENT 5 — REPORTER AGENT
# Writes the final professional report
# ══════════════════════════════════════════════════════════════
def reporter_agent(profile: dict, strategy: str,
                   execution_result: str, validation: str,
                   model_score: str) -> str:
    print("\n" + "="*55)
    print("📝 REPORTER AGENT — Writing final report...")
    print("="*55)

    prompt = f"""
You are a professional data scientist writing a report for a business client.

DATASET INFO:
- Size: {profile['shape'][0]:,} rows × {profile['shape'][1]} columns
- Target: {profile['likely_target']}
- Task: {profile['target_type']}
- Model Score: {model_score}

ML STRATEGY USED:
{strategy[:800]}

MODEL RESULTS:
{execution_result[:800]}

VALIDATION FINDINGS:
{validation[:800]}

Write a PROFESSIONAL ML REPORT with these exact sections:

# 🤖 AutoGen ML Analysis Report

## 📊 Executive Summary
(3 sentences: what was analyzed, what model was built, key result)

## 🔍 Dataset Overview
(bullet points: size, features, target variable, data quality)

## 🧠 ML Strategy
(what approach was taken and why — explain like a business person)

## ⚙️ Model Results
(the actual numbers, what they mean in plain English)

## ✅ Validation & Quality
(is the model trustworthy? key concerns?)

## 🚀 Recommendations
(3 specific next steps for improving or deploying this model)

## 💡 Business Insights
(what does this model mean for the actual business decision?)

Write professionally. Use the actual numbers. Be specific.
    """

    response = llm.invoke(prompt)
    report = response.content

    print("   ✓ Report written")

    return report


# ══════════════════════════════════════════════════════════════
# ORCHESTRATOR — Connects all 5 agents
# ══════════════════════════════════════════════════════════════
def run_autogen_pipeline(file_path: str):
    print("\n" + "🔥"*27)
    print("   AUTOGEN DATA SCIENCE PIPELINE — 5 AGENTS")
    print("🔥"*27)

    # Agent 1: Explore
    explorer_result = explorer_agent(file_path)
    if explorer_result["status"] == "error":
        print(f"\n❌ Explorer failed: {explorer_result['error']}")
        return

    profile = explorer_result["profile"]

    # Agent 2: Strategy
    strategy_result = strategy_agent(profile)
    if strategy_result["status"] == "error":
        print(f"\n❌ Strategy failed")
        return

    strategy = strategy_result["strategy"]

    # Agent 3: Build + Run
    builder_result = builder_agent(file_path, profile, strategy)
    if builder_result["status"] == "error":
        print(f"\n❌ Builder failed")
        return

    # Agent 4: Validate
    validator_result = validator_agent(
        builder_result["code"],
        builder_result["execution_result"],
        profile
    )

    # Agent 5: Report
    final_report = reporter_agent(
        profile,
        strategy,
        builder_result["execution_result"],
        validator_result["validation"],
        builder_result["model_score"]
    )

    # ── Final Output ──────────────────────────────────────────
    print("\n" + "="*55)
    print("   🎯 PIPELINE COMPLETE — FINAL REPORT")
    print("="*55)

    full_output = f"""
{'='*55}
AUTOGEN DS PIPELINE — COMPLETE REPORT
{'='*55}

{final_report}

{'='*55}
GENERATED ML CODE
{'='*55}
{builder_result['code']}

{'='*55}
CODE EXECUTION OUTPUT
{'='*55}
{builder_result['execution_result']}

{'='*55}
VALIDATION NOTES
{'='*55}
{validator_result['validation']}
    """

    print(final_report)

    # Save everything
    output_file = f"autogen_report_{file_path.split('\\')[-1].replace('.csv','')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_output)

    print(f"\n✅ Full report saved to: {output_file}")
    print(f"✅ Model Score: {builder_result['model_score']}")


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("="*55)
    print("   🤖 AUTOGEN DATA SCIENCE AGENT")
    print("   5 AI agents building your ML pipeline")
    print("="*55)

    file = input("\nEnter CSV file path: ").strip()
    run_autogen_pipeline(file)