import streamlit as st
import os
import tempfile
import pandas as pd
from datetime import datetime

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AgentIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; }
.stApp { background: #080810; }
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0d18 !important;
    border-right: 1px solid #1e1e30 !important;
}

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0f0f1f 0%, #1a1040 50%, #0f1f3d 100%);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 50% 50%, rgba(139,92,246,0.06) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 44px;
    font-weight: 700;
    background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
    line-height: 1.2;
}
.hero-sub {
    color: #64748b;
    font-size: 16px;
    margin: 0;
}

/* Agent cards */
.agent-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 28px; }
.agent-card {
    background: #0d0d18;
    border: 1.5px solid #1e1e30;
    border-radius: 16px;
    padding: 22px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}
.agent-card:hover { border-color: #7c3aed; transform: translateY(-2px); }
.agent-card.active {
    border-color: #7c3aed;
    background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(96,165,250,0.06));
    box-shadow: 0 0 24px rgba(124,58,237,0.15);
}
.agent-icon { font-size: 32px; margin-bottom: 10px; }
.agent-name { color: #e2e8f0; font-size: 15px; font-weight: 600; margin-bottom: 6px; }
.agent-desc { color: #475569; font-size: 12px; line-height: 1.5; }

/* Quick prompts */
.prompt-chip {
    display: inline-block;
    background: #0d0d18;
    border: 1px solid #1e1e30;
    border-radius: 100px;
    padding: 7px 16px;
    color: #64748b;
    font-size: 12px;
    margin: 4px;
    cursor: pointer;
    transition: all 0.15s;
}
.prompt-chip:hover { border-color: #7c3aed; color: #a78bfa; }

/* Input */
.stTextArea textarea {
    background: #0d0d18 !important;
    border: 1.5px solid #1e1e30 !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 14px !important;
    padding: 14px !important;
}
.stTextArea textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
}

/* Run button */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(124,58,237,0.4) !important;
}

/* Output */
.output-container {
    background: #0d0d18;
    border: 1px solid #1e1e30;
    border-radius: 16px;
    padding: 28px 32px;
    margin-top: 20px;
}
.output-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #1e1e30;
}
.output-badge {
    background: rgba(124,58,237,0.12);
    color: #a78bfa;
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 600;
}

/* History item */
.history-item {
    background: #0d0d18;
    border: 1px solid #1e1e30;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.15s;
}
.history-item:hover { border-color: #7c3aed; }
.history-task { color: #94a3b8; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.history-meta { color: #334155; font-size: 11px; margin-top: 4px; }

/* Steps */
.steps-row { display: flex; gap: 10px; margin: 16px 0; }
.step {
    flex: 1; background: #0d0d18;
    border: 1px solid #1e1e30;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    font-size: 13px;
    color: #334155;
    transition: all 0.3s;
}
.step.active { border-color: #7c3aed; color: #a78bfa; background: rgba(124,58,237,0.06); }
.step.done { border-color: #059669; color: #34d399; background: rgba(5,150,105,0.06); }

/* Section label */
.section-label {
    color: #475569;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
    margin-top: 4px;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #0d0d18 !important;
    border: 1.5px dashed #1e1e30 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = "Research Writer"
if "task_text" not in st.session_state:
    st.session_state.task_text = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "last_output" not in st.session_state:
    st.session_state.last_output = None

# ── Agent Config ──────────────────────────────────────────────
AGENTS = {
    "Data Analyst": {
        "icon": "📊",
        "desc": "Upload CSV → instant professional analysis with insights & recommendations",
        "needs_csv": True,
        "route": "DATA",
        "prompts": [
            "Find patterns and anomalies in this dataset",
            "Give me a full statistical summary",
            "Identify data quality issues and missing values",
            "What are the top insights from this data?"
        ]
    },
    "Research Writer": {
        "icon": "🌐",
        "desc": "Any topic → researched, structured 600+ word professional report",
        "needs_csv": False,
        "route": "RESEARCH",
        "prompts": [
            "Future of AI agents in enterprise software",
            "Latest trends in generative AI 2025",
            "How startups are monetizing LLMs",
            "Impact of automation on jobs in India",
            "Best practices in MLOps for small teams"
        ]
    },
    "Code Generator": {
        "icon": "💻",
        "desc": "Describe any task → working, tested Python code with full explanation",
        "needs_csv": False,
        "route": "CODE",
        "prompts": [
            "Build a web scraper for news articles",
            "Create a data visualization with charts",
            "Write a CSV cleaner that removes duplicates",
            "Build a REST API with FastAPI",
            "Create a machine learning pipeline with sklearn"
        ]
    },
    "Summarizer": {
        "icon": "✂️",
        "desc": "Paste any long text, article or report → clean concise summary",
        "needs_csv": False,
        "route": "SUMMARIZE",
        "prompts": [
            "Summarize this research paper",
            "Give me key points from this article",
            "Extract action items from this text",
            "Simplify this technical document"
        ]
    },
    "Email Writer": {
        "icon": "✉️",
        "desc": "Describe situation → professional email ready to send",
        "needs_csv": False,
        "route": "EMAIL",
        "prompts": [
            "Write a cold outreach email to a startup founder",
            "Follow up email after a job interview",
            "Request for project extension from manager",
            "Professional introduction email to a new team"
        ]
    },
    "SEO Writer": {
        "icon": "🔍",
        "desc": "Topic + keywords → SEO optimized blog post or content",
        "needs_csv": False,
        "route": "SEO",
        "prompts": [
            "Write an SEO blog post about AI tools for freelancers",
            "Create meta descriptions for a data science website",
            "Write a product description for an AI SaaS tool",
            "SEO article about Python for beginners"
        ]
    }
}

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 20px 0;">
        <div style="font-size:22px; font-weight:700; color:#e2e8f0;">🧠 AgentIQ</div>
        <div style="font-size:12px; color:#334155; margin-top:4px;">Multi-Agent AI Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Chat History</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div style="color:#334155; font-size:13px; padding:16px;
        border:1px dashed #1e1e30; border-radius:10px; text-align:center;">
            No history yet.<br>Run your first task!
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
            if st.button(
                f"{item['icon']} {item['task'][:35]}{'...' if len(item['task'])>35 else ''}",
                key=f"hist_{i}",
                use_container_width=True
            ):
                st.session_state.last_output = item
                st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="color:#1e293b; font-size:11px; line-height:1.8;">
    Powered by LangGraph + Groq LLaMA 3<br>
    © 2025 AgentIQ
    </div>
    """, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">🧠 AgentIQ</div>
    <p class="hero-sub">6 specialized AI agents — pick one, describe your task, get professional output instantly</p>
</div>
""", unsafe_allow_html=True)

# ── Step 1: Agent Selection ───────────────────────────────────
st.markdown('<div class="section-label">Step 1 — Choose your agent</div>', unsafe_allow_html=True)

agent_names = list(AGENTS.keys())
cols = st.columns(6)

for i, name in enumerate(agent_names):
    with cols[i]:
        agent = AGENTS[name]
        is_active = st.session_state.selected_agent == name
        active_class = "active" if is_active else ""
        st.markdown(f"""
        <div class="agent-card {active_class}">
            <div class="agent-icon">{agent['icon']}</div>
            <div class="agent-name">{name}</div>
            <div class="agent-desc">{agent['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select", key=f"agent_{i}", use_container_width=True):
            st.session_state.selected_agent = name
            st.session_state.task_text = ""
            st.rerun()

selected_name = st.session_state.selected_agent
selected = AGENTS[selected_name]

st.markdown("<br>", unsafe_allow_html=True)

# ── Step 2: Quick Prompts + Task Input ───────────────────────
st.markdown('<div class="section-label">Step 2 — Pick a quick prompt or write your own</div>', unsafe_allow_html=True)

prompt_cols = st.columns(min(len(selected["prompts"]), 3))
for i, prompt in enumerate(selected["prompts"]):
    with prompt_cols[i % 3]:
        if st.button(f"💡 {prompt[:38]}{'...' if len(prompt)>38 else ''}", key=f"p_{i}", use_container_width=True):
            st.session_state.task_text = prompt
            st.rerun()

task_input = st.text_area(
    label="task",
    value=st.session_state.task_text,
    placeholder=f"Describe your task for the {selected_name} agent...",
    height=120,
    label_visibility="collapsed"
)

# ── Step 3: CSV Upload ────────────────────────────────────────
uploaded_file = None
if selected["needs_csv"]:
    st.markdown('<div class="section-label" style="margin-top:16px;">Step 3 — Upload your CSV</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("CSV", type=["csv"], label_visibility="collapsed")
    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} — {uploaded_file.size // 1024} KB ready")

# ── Summarizer: text input ────────────────────────────────────
paste_text = None
if selected["route"] == "SUMMARIZE":
    st.markdown('<div class="section-label" style="margin-top:16px;">Step 3 — Paste your text</div>', unsafe_allow_html=True)
    paste_text = st.text_area(
        "paste",
        placeholder="Paste the article, document, or text you want summarized here...",
        height=180,
        label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Run Button ────────────────────────────────────────────────
run = st.button(f"🚀 Run {selected_name} Agent", use_container_width=True)

# ── Show last output from history ────────────────────────────
if st.session_state.last_output and not run:
    item = st.session_state.last_output
    st.markdown(f"""
    <div class="output-container">
        <div class="output-header">
            <span style="font-size:20px;">{item['icon']}</span>
            <span class="output-badge">{item['agent']}</span>
            <span style="color:#334155; font-size:12px; margin-left:auto;">{item['time']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(item["output"])

# ── Processing ────────────────────────────────────────────────
if run:
    final_task = task_input.strip()
    if selected["route"] == "SUMMARIZE" and paste_text:
        final_task = f"Summarize this text: {paste_text[:3000]}"

    if not final_task:
        st.error("Please enter a task or pick a quick prompt.")
    elif selected["needs_csv"] and not uploaded_file:
        st.error("Please upload a CSV file for the Data Analyst agent.")
    else:
        # Save CSV
        temp_file_path = None
        if uploaded_file:
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            df = pd.read_csv(uploaded_file)
            df.to_csv(temp_file_path, index=False)

        # Progress
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            s1 = st.empty()
            s1.markdown('<div class="step active">🤔 Understanding task</div>', unsafe_allow_html=True)
        with c2:
            s2 = st.empty()
            s2.markdown('<div class="step">⏳ Agent working</div>', unsafe_allow_html=True)
        with c3:
            s3 = st.empty()
            s3.markdown('<div class="step">⏳ Preparing output</div>', unsafe_allow_html=True)

        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
            )

            s1.markdown('<div class="step done">✅ Task understood</div>', unsafe_allow_html=True)
            s2.markdown('<div class="step active">🤖 Agent working...</div>', unsafe_allow_html=True)

            output = ""
            route = selected["route"]

            # ── EMAIL agent ───────────────────────────────────
            if route == "EMAIL":
                prompt = f"""
You are an expert professional email writer.
Write a complete, ready-to-send professional email for this situation:
{final_task}

Format:
**Subject:** [subject line]

**Email:**
[full email body]

**Tone:** Professional, warm, and concise.
Make it genuine, not generic. Under 200 words.
                """
                response = llm.invoke(prompt)
                output = response.content

            # ── SEO agent ────────────────────────────────────
            elif route == "SEO":
                prompt = f"""
You are an expert SEO content writer.
Write high-quality, SEO-optimized content for:
{final_task}

Include:
**Title:** (compelling, keyword-rich)
**Meta Description:** (150-160 chars)
**Content:** (600-800 words, structured with H2 subheadings)
**Keywords used:** (list 5-8 keywords naturally used)
**Call to Action:** (1 strong CTA at the end)

Write naturally, not keyword-stuffed.
                """
                response = llm.invoke(prompt)
                output = response.content

            # ── SUMMARIZE agent ───────────────────────────────
            elif route == "SUMMARIZE":
                prompt = f"""
You are an expert at summarizing and extracting key information.
Task: {final_task}

Provide:
**TL;DR:** (2-sentence summary)

**Key Points:**
(5-7 bullet points with the most important information)

**Important Details:**
(any numbers, dates, names, or facts worth remembering)

**Conclusion:**
(1 paragraph on the main takeaway)

Be concise but don't miss anything important.
                """
                response = llm.invoke(prompt)
                output = response.content

            # ── DATA, RESEARCH, CODE agents ───────────────────
            else:
                from orchestrator import build_orchestrator
                orchestrator = build_orchestrator()
                result = orchestrator.invoke({
                    "user_task": final_task,
                    "route": "",
                    "file_path": temp_file_path,
                    "final_output": "",
                    "error": None
                })
                output = result["final_output"]

            s2.markdown('<div class="step done">✅ Agent completed</div>', unsafe_allow_html=True)
            s3.markdown('<div class="step done">✅ Output ready</div>', unsafe_allow_html=True)

            # Save to history
            history_item = {
                "icon": selected["icon"],
                "agent": selected_name,
                "task": final_task,
                "output": output,
                "time": datetime.now().strftime("%H:%M")
            }
            st.session_state.history.append(history_item)
            st.session_state.last_output = history_item

            # Display output
            st.markdown(f"""
            <div class="output-container">
                <div class="output-header">
                    <span style="font-size:20px;">{selected['icon']}</span>
                    <span class="output-badge">{selected_name} Agent</span>
                    <span style="color:#334155; font-size:12px; margin-left:auto;">
                        {datetime.now().strftime("%H:%M")}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(output)

            st.download_button(
                "⬇️ Download Output",
                data=output,
                file_name=f"agentiq_{route.lower()}_{datetime.now().strftime('%H%M')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            s1.empty(); s2.empty(); s3.empty()
            st.error(f"Error: {str(e)}")