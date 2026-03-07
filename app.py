import streamlit as st
import os
import tempfile
import pandas as pd

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AgentIQ — Multi-Agent AI Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #0f0f13; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 20px;
        padding: 44px 40px;
        text-align: center;
        margin-bottom: 28px;
        border: 1px solid rgba(99,102,241,0.2);
    }
    .hero h1 {
        font-size: 40px;
        font-weight: 700;
        background: linear-gradient(135deg, #fff 0%, #818cf8 60%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .hero p { color: #94a3b8; font-size: 16px; margin: 0; }

    .section-label {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 10px;
        margin-top: 4px;
    }

    /* Agent selector tabs */
    .agent-tab {
        background: #1e1e2e;
        border: 1.5px solid #2d2d3d;
        border-radius: 12px;
        padding: 16px;
        cursor: pointer;
        text-align: center;
        transition: all 0.2s;
    }
    .agent-tab:hover { border-color: #6366f1; }
    .agent-tab.selected { border-color: #6366f1; background: rgba(99,102,241,0.12); }
    .agent-tab .icon { font-size: 26px; margin-bottom: 6px; }
    .agent-tab .name { color: #e2e8f0; font-size: 14px; font-weight: 600; }
    .agent-tab .desc { color: #64748b; font-size: 12px; margin-top: 4px; line-height: 1.4; }

    /* Quick prompt chips */
    .chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
    .chip {
        background: #1e1e2e;
        border: 1px solid #2d2d3d;
        border-radius: 100px;
        padding: 6px 14px;
        color: #94a3b8;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.15s;
        white-space: nowrap;
    }
    .chip:hover { border-color: #6366f1; color: #818cf8; }

    /* Output */
    .output-box {
        background: #1e1e2e;
        border: 1px solid #2d2d3d;
        border-radius: 14px;
        padding: 28px;
        margin-top: 16px;
        white-space: pre-wrap;
        color: #e2e8f0;
        font-size: 14px;
        line-height: 1.8;
        max-height: 620px;
        overflow-y: auto;
    }

    /* Sidebar agent cards */
    .agent-card {
        background: #1e1e2e;
        border: 1px solid #2d2d3d;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
    }
    .agent-card h4 { color: #e2e8f0; font-size: 14px; font-weight: 600; margin-bottom: 4px; }
    .agent-card p { color: #64748b; font-size: 12px; margin: 0; line-height: 1.5; }

    /* Run button */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        width: 100% !important;
    }
    .stButton > button:hover { opacity: 0.88 !important; }

    .stTextArea textarea {
        background: #1e1e2e !important;
        border: 1px solid #2d2d3d !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-size: 14px !important;
    }

    .step-row {
        display: flex;
        gap: 12px;
        margin: 16px 0;
    }
    .step-box {
        flex: 1;
        background: #1e1e2e;
        border: 1px solid #2d2d3d;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        font-size: 13px;
        color: #475569;
    }
    .step-box.active { border-color: #6366f1; color: #818cf8; }
    .step-box.done { border-color: #22c55e; color: #4ade80; }
</style>
""", unsafe_allow_html=True)

# ── Quick prompts per agent ───────────────────────────────────
QUICK_PROMPTS = {
    "📊 Data Analyst": [
        "Find patterns and anomalies in my dataset",
        "Give me a full statistical summary",
        "Identify missing values and data quality issues",
        "What are the key insights from this data?",
    ],
    "🌐 Research Writer": [
        "Research the future of AI in healthcare",
        "Latest trends in generative AI 2025",
        "Impact of climate change on global economy",
        "How are startups using LLMs to make money?",
        "Best practices in data science for beginners",
    ],
    "💻 Code Generator": [
        "Write a Python web scraper for news articles",
        "Build a student grade calculator with averages",
        "Create a data visualization dashboard with charts",
        "Write a CSV file cleaner that removes duplicates",
        "Build a simple chatbot using Python",
    ]
}

AGENT_INFO = {
    "📊 Data Analyst": {
        "desc": "Upload any CSV file and get a full professional analysis report — patterns, insights, recommendations.",
        "needs_csv": True,
        "placeholder": "Describe what you want to know about your data, or pick a quick prompt above.",
        "route": "DATA"
    },
    "🌐 Research Writer": {
        "desc": "Type any topic and get a researched, structured 500+ word report with findings and insights.",
        "needs_csv": False,
        "placeholder": "Enter a topic to research, or pick a quick prompt above.",
        "route": "RESEARCH"
    },
    "💻 Code Generator": {
        "desc": "Describe any coding task and get working, tested Python code with a full explanation.",
        "needs_csv": False,
        "placeholder": "Describe what you want to build, or pick a quick prompt above.",
        "route": "CODE"
    }
}

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 AgentIQ")
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("""
    <div style="color:#64748b; font-size:13px; line-height:1.8;">
    1. Pick an agent below<br>
    2. Choose a quick prompt or type your own<br>
    3. Hit Run — get your output in seconds
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Agents**")
    for name, info in AGENT_INFO.items():
        st.markdown(f"""
        <div class="agent-card">
            <h4>{name}</h4>
            <p>{info['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="color:#334155; font-size:11px; line-height:1.6;">
    Powered by LangGraph + Groq LLaMA 3<br>
    © 2025 AgentIQ
    </div>
    """, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🧠 AgentIQ</h1>
    <p>Pick an agent, choose a task — get professional AI output in seconds</p>
</div>
""", unsafe_allow_html=True)

# ── Step 1: Pick Agent ────────────────────────────────────────
st.markdown('<div class="section-label">Step 1 — Choose your agent</div>', unsafe_allow_html=True)

agent_names = list(AGENT_INFO.keys())
cols = st.columns(3)

# Track selected agent in session state
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = agent_names[0]

for i, name in enumerate(agent_names):
    with cols[i]:
        is_selected = st.session_state.selected_agent == name
        border = "border: 1.5px solid #6366f1; background: rgba(99,102,241,0.1);" if is_selected else "border: 1.5px solid #2d2d3d;"
        icons = ["📊", "🌐", "💻"]
        descs = ["Analyze CSV data", "Research any topic", "Generate Python code"]
        st.markdown(f"""
        <div style="background:#1e1e2e; {border} border-radius:12px; padding:18px; text-align:center; cursor:pointer;">
            <div style="font-size:28px; margin-bottom:8px;">{icons[i]}</div>
            <div style="color:#e2e8f0; font-size:14px; font-weight:600;">{name.split(' ', 1)[1]}</div>
            <div style="color:#64748b; font-size:12px; margin-top:4px;">{descs[i]}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Select", key=f"sel_{i}", use_container_width=True):
            st.session_state.selected_agent = name
            st.session_state.task_text = ""
            st.rerun()

selected = st.session_state.selected_agent
selected_info = AGENT_INFO[selected]

st.markdown("<br>", unsafe_allow_html=True)

# ── Step 2: Quick Prompts ─────────────────────────────────────
st.markdown('<div class="section-label">Step 2 — Pick a quick task or write your own</div>', unsafe_allow_html=True)

if "task_text" not in st.session_state:
    st.session_state.task_text = ""

# Show quick prompt buttons
prompts = QUICK_PROMPTS[selected]
num_cols = min(len(prompts), 3)
prompt_cols = st.columns(num_cols)

for i, prompt in enumerate(prompts):
    with prompt_cols[i % num_cols]:
        if st.button(f"💡 {prompt[:35]}{'...' if len(prompt)>35 else ''}", key=f"prompt_{i}", use_container_width=True):
            st.session_state.task_text = prompt
            st.rerun()

# Task text area
task_input = st.text_area(
    label="Your task",
    value=st.session_state.task_text,
    placeholder=selected_info["placeholder"],
    height=110,
    label_visibility="collapsed",
    key="task_area"
)

# ── Step 3: CSV Upload (only for Data Analyst) ────────────────
uploaded_file = None
if selected_info["needs_csv"]:
    st.markdown('<div class="section-label" style="margin-top:16px;">Step 3 — Upload your CSV file</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} uploaded — {uploaded_file.size // 1024} KB")

st.markdown("<br>", unsafe_allow_html=True)

# ── Run Button ────────────────────────────────────────────────
run_clicked = st.button("🚀 Run AgentIQ", use_container_width=True)

# ── Output ────────────────────────────────────────────────────
if run_clicked:
    final_task = task_input.strip()

    if not final_task:
        st.error("Please enter a task or pick a quick prompt above.")
    elif selected_info["needs_csv"] and not uploaded_file:
        st.error("Please upload a CSV file for the Data Analyst agent.")
    else:
        # Save CSV temporarily
        temp_file_path = None
        if uploaded_file:
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            df = pd.read_csv(uploaded_file)
            df.to_csv(temp_file_path, index=False)

        # Progress UI
        st.markdown("---")
        st.markdown("**⚡ Running your agents...**")

        c1, c2, c3 = st.columns(3)
        with c1:
            p1 = st.empty()
            p1.markdown('<div class="step-box active">🤔 Understanding task</div>', unsafe_allow_html=True)
        with c2:
            p2 = st.empty()
            p2.markdown('<div class="step-box">⏳ Agent working</div>', unsafe_allow_html=True)
        with c3:
            p3 = st.empty()
            p3.markdown('<div class="step-box">⏳ Preparing output</div>', unsafe_allow_html=True)

        try:
            from orchestrator import build_orchestrator

            # Force correct route based on selected agent
            route_map = {"📊 Data Analyst": "DATA", "🌐 Research Writer": "RESEARCH", "💻 Code Generator": "CODE"}
            forced_route = route_map[selected]

            p1.markdown('<div class="step-box done">✅ Task understood</div>', unsafe_allow_html=True)
            p2.markdown('<div class="step-box active">🤖 Agent working...</div>', unsafe_allow_html=True)

            orchestrator = build_orchestrator()
            result = orchestrator.invoke({
                "user_task": final_task,
                "route": "",
                "file_path": temp_file_path,
                "final_output": "",
                "error": None
            })

            p2.markdown('<div class="step-box done">✅ Agent completed</div>', unsafe_allow_html=True)
            p3.markdown('<div class="step-box done">✅ Output ready</div>', unsafe_allow_html=True)

            # Result
            st.markdown(f"""
            <div style="margin-top:20px; margin-bottom:10px;">
                <span style="background:rgba(99,102,241,0.1); color:#818cf8; padding:5px 16px;
                border-radius:100px; font-size:13px; font-weight:600; border:1px solid rgba(99,102,241,0.25);">
                    ✓ Handled by: {selected}
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📄 Your Output")
            st.markdown(
                f'<div class="output-box">{result["final_output"]}</div>',
                unsafe_allow_html=True
            )

            st.download_button(
                label="⬇️ Download Output",
                data=result["final_output"],
                file_name=f"agentiq_{forced_route.lower()}_output.txt",
                mime="text/plain"
            )

        except Exception as e:
            p1.empty(); p2.empty(); p3.empty()
            st.error(f"Error: {str(e)}")