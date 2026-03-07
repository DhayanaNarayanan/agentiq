import streamlit as st
import os
import tempfile
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="AgentIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp { font-family: 'DM Sans', sans-serif !important; background: #03030a !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { background: #05050f !important; border-right: 1px solid rgba(255,255,255,0.04) !important; }

.bg-orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.18; animation: float 12s ease-in-out infinite; }
.orb1 { width: 500px; height: 500px; background: radial-gradient(circle, #6d28d9, transparent); top: -150px; left: -100px; animation-delay: 0s; }
.orb2 { width: 400px; height: 400px; background: radial-gradient(circle, #0ea5e9, transparent); top: 20%; right: -100px; animation-delay: -4s; }
.orb3 { width: 350px; height: 350px; background: radial-gradient(circle, #7c3aed, transparent); bottom: -100px; left: 30%; animation-delay: -8s; }
.orb4 { width: 250px; height: 250px; background: radial-gradient(circle, #06b6d4, transparent); top: 60%; left: 10%; animation-delay: -6s; }

@keyframes float {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -30px) scale(1.05); }
    66% { transform: translate(-20px, 20px) scale(0.95); }
}

.hero-wrap {
    position: relative; text-align: center;
    padding: 64px 20px 52px; margin-bottom: 44px;
}
.hero-ring {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    border-radius: 50%; pointer-events: none;
    border: 1px solid rgba(109,40,217,0.12);
    animation: ring-pulse 4s ease-in-out infinite;
}
.r1 { width: 280px; height: 280px; }
.r2 { width: 420px; height: 420px; animation-delay: -1.4s; border-color: rgba(14,165,233,0.07); }
.r3 { width: 560px; height: 560px; animation-delay: -2.8s; border-color: rgba(109,40,217,0.04); }
.r4 { width: 700px; height: 700px; animation-delay: -4.2s; border-color: rgba(14,165,233,0.03); }

@keyframes ring-pulse {
    0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
    50% { opacity: 1; transform: translate(-50%, -50%) scale(1.02); }
}

.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(109,40,217,0.08); border: 1px solid rgba(109,40,217,0.2);
    border-radius: 100px; padding: 7px 20px;
    font-size: 11px; font-weight: 500; color: #a78bfa;
    letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 28px; animation: fade-up 0.6s ease both;
}
.hero-badge-dot { width: 6px; height: 6px; background: #a78bfa; border-radius: 50%; animation: blink 2s ease infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.2;} }

.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(52px, 8vw, 88px);
    font-weight: 800; line-height: 1; letter-spacing: -3px;
    background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 35%, #38bdf8 70%, #c4b5fd 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: shimmer 8s linear infinite, fade-up 0.8s ease both 0.1s;
    margin-bottom: 20px;
}
@keyframes shimmer { 0%{background-position:0% 50%;} 100%{background-position:300% 50%;} }

.hero-sub {
    font-size: 17px; color: #334155; font-weight: 400; line-height: 1.7;
    max-width: 480px; margin: 0 auto 36px;
    animation: fade-up 0.8s ease both 0.2s;
}
.hero-stats {
    display: flex; justify-content: center; gap: 48px;
    animation: fade-up 0.8s ease both 0.3s;
}
.stat { text-align: center; }
.stat-num {
    font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800;
    background: linear-gradient(135deg, #c4b5fd, #38bdf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-label { color: #1e293b; font-size: 11px; margin-top: 3px; letter-spacing: 1px; text-transform: uppercase; }

@keyframes fade-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.sec-label {
    font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 600;
    letter-spacing: 3px; text-transform: uppercase; color: #1e293b;
    margin-bottom: 14px; margin-top: 6px;
    display: flex; align-items: center; gap: 12px;
}
.sec-label::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.03); }

.agent-card {
    background: rgba(255,255,255,0.015);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 18px; padding: 22px 14px;
    text-align: center; position: relative; overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    min-height: 150px;
}
.agent-card::after {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(circle at 50% 0%, rgba(109,40,217,0.1), transparent 65%);
    opacity: 0; transition: opacity 0.3s;
}
.agent-card:hover { border-color: rgba(109,40,217,0.35); transform: translateY(-5px); box-shadow: 0 24px 64px rgba(109,40,217,0.12); }
.agent-card:hover::after { opacity: 1; }
.agent-card.active {
    border-color: rgba(109,40,217,0.5);
    background: linear-gradient(135deg, rgba(109,40,217,0.08), rgba(14,165,233,0.04));
    box-shadow: 0 0 48px rgba(109,40,217,0.18), inset 0 1px 0 rgba(255,255,255,0.06);
}
.agent-card.active::after { opacity: 1; }

.agent-icon-box {
    width: 50px; height: 50px; border-radius: 13px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 12px; font-size: 22px;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.3s; position: relative; z-index: 1;
}
.agent-card:hover .agent-icon-box, .agent-card.active .agent-icon-box {
    background: rgba(109,40,217,0.15); border-color: rgba(109,40,217,0.3);
    transform: scale(1.1) rotate(-3deg);
}
.a-name { font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700; color: #e2e8f0; margin-bottom: 6px; position: relative; z-index: 1; }
.a-desc { font-size: 11px; color: #1e293b; line-height: 1.5; position: relative; z-index: 1; }

.stTextArea textarea {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important; color: #94a3b8 !important;
    font-size: 14px !important; font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: rgba(109,40,217,0.45) !important;
    box-shadow: 0 0 0 4px rgba(109,40,217,0.07) !important;
    color: #e2e8f0 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #6d28d9, #4338ca, #0ea5e9) !important;
    background-size: 200% !important;
    color: white !important; border: none !important;
    border-radius: 14px !important; padding: 15px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    letter-spacing: 0.5px !important; width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 6px 28px rgba(109,40,217,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 40px rgba(109,40,217,0.45) !important;
}

.step-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 12px; padding: 14px 10px;
    text-align: center; font-size: 13px; color: #1e293b;
    transition: all 0.35s ease;
}
.step-item.active {
    border-color: rgba(109,40,217,0.4); color: #a78bfa;
    background: rgba(109,40,217,0.07);
    animation: pulse-glow 1.5s ease infinite;
}
.step-item.done { border-color: rgba(16,185,129,0.35); color: #34d399; background: rgba(16,185,129,0.05); }
@keyframes pulse-glow {
    0%,100%{box-shadow:0 0 16px rgba(109,40,217,0.1);}
    50%{box-shadow:0 0 32px rgba(109,40,217,0.25);}
}

.output-card {
    background: rgba(255,255,255,0.018);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px; padding: 32px 36px;
    margin-top: 28px; position: relative; overflow: hidden;
    animation: fade-up 0.5s ease both;
}
.output-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #6d28d9, #0ea5e9, #6d28d9, transparent);
    background-size: 200%;
    animation: top-line 3s linear infinite;
}
@keyframes top-line { 0%{background-position:0%} 100%{background-position:200%} }

.out-meta {
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    padding-bottom: 20px; margin-bottom: 24px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.out-badge {
    background: rgba(109,40,217,0.1); border: 1px solid rgba(109,40,217,0.22);
    border-radius: 100px; padding: 5px 16px;
    font-family: 'Syne', sans-serif; font-size: 11px; font-weight: 700;
    color: #a78bfa; letter-spacing: 1px; text-transform: uppercase;
}
.out-task {
    color: #334155; font-size: 12px;
    background: rgba(255,255,255,0.025); padding: 5px 14px;
    border-radius: 100px; border: 1px solid rgba(255,255,255,0.04);
    max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.out-time { color: #1e293b; font-size: 11px; margin-left: auto; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: rgba(109,40,217,0.25); border-radius: 4px; }
</style>

<div class="bg-orbs">
    <div class="orb orb1"></div>
    <div class="orb orb2"></div>
    <div class="orb orb3"></div>
    <div class="orb orb4"></div>
</div>
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

AGENTS = {
    "Data Analyst":    {"icon":"📊","desc":"Upload CSV → instant professional analysis","needs_csv":True,"route":"DATA","prompts":["Find patterns and anomalies","Full statistical summary","Identify data quality issues","Top insights from this data"]},
    "Research Writer": {"icon":"🌐","desc":"Topic → 600+ word researched report","needs_csv":False,"route":"RESEARCH","prompts":["Future of AI agents in enterprise","Latest trends in GenAI 2025","How startups monetize LLMs","Impact of automation on jobs"]},
    "Code Generator":  {"icon":"💻","desc":"Describe task → working Python code","needs_csv":False,"route":"CODE","prompts":["Web scraper for news articles","Data visualization with charts","REST API with FastAPI","ML pipeline with sklearn"]},
    "Summarizer":      {"icon":"✂️","desc":"Long text → clean concise summary","needs_csv":False,"route":"SUMMARIZE","prompts":["Summarize this research paper","Key points from this article","Extract action items","Simplify technical document"]},
    "Email Writer":    {"icon":"✉️","desc":"Situation → professional email","needs_csv":False,"route":"EMAIL","prompts":["Cold outreach to startup founder","Follow up after job interview","Request project extension","Introduction to new team"]},
    "SEO Writer":      {"icon":"🔍","desc":"Topic → SEO optimized content","needs_csv":False,"route":"SEO","prompts":["SEO blog post about AI tools","Meta descriptions for DS site","Product description for SaaS","SEO article Python beginners"]},
}

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 4px 28px;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
        background:linear-gradient(135deg,#c4b5fd,#38bdf8);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">🧠 AgentIQ</div>
        <div style="font-size:10px;color:#1e293b;margin-top:5px;letter-spacing:3px;text-transform:uppercase;">Multi-Agent Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label">History</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""<div style="text-align:center;padding:28px 12px;
        border:1px dashed rgba(255,255,255,0.04);border-radius:12px;color:#1e293b;font-size:12px;line-height:2;">
        ✦ No history yet<br><span style="font-size:11px;color:#0f172a;">Run your first task</span></div>""", unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            if st.button(f"{item['icon']} {item['task'][:26]}{'…' if len(item['task'])>26 else ''}", key=f"h_{i}", use_container_width=True):
                st.session_state.last_output = item
                st.rerun()

    st.markdown("---")
    st.markdown("""<div style="color:#0f172a;font-size:11px;line-height:2.2;">
    ⚡ LangGraph · Groq LLaMA 3<br>🔒 Data stays private<br>🌍 6 specialized agents<br>
    <span style="color:#1e293b;margin-top:8px;display:block;">© 2025 AgentIQ</span></div>""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-ring r1"></div>
    <div class="hero-ring r2"></div>
    <div class="hero-ring r3"></div>
    <div class="hero-ring r4"></div>
    <div class="hero-badge"><div class="hero-badge-dot"></div>Powered by LLaMA 3 · LangGraph</div>
    <div class="hero-title">AgentIQ</div>
    <p class="hero-sub">Six AI agents working in concert — analyze data, research topics, generate code, write emails and more.</p>
    <div class="hero-stats">
        <div class="stat"><div class="stat-num">6</div><div class="stat-label">AI Agents</div></div>
        <div class="stat"><div class="stat-num">∞</div><div class="stat-label">Tasks</div></div>
        <div class="stat"><div class="stat-num">~10s</div><div class="stat-label">Per Output</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Agent Selection ───────────────────────────────────────────
st.markdown('<div class="sec-label">Choose your agent</div>', unsafe_allow_html=True)

cols = st.columns(6)
for i, (name, ag) in enumerate(AGENTS.items()):
    with cols[i]:
        active = "active" if st.session_state.selected_agent == name else ""
        st.markdown(f"""
        <div class="agent-card {active}">
            <div class="agent-icon-box">{ag['icon']}</div>
            <div class="a-name">{name}</div>
            <div class="a-desc">{ag['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select", key=f"sel_{i}", use_container_width=True):
            st.session_state.selected_agent = name
            st.session_state.task_text = ""
            st.rerun()

selected_name = st.session_state.selected_agent
selected = AGENTS[selected_name]
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Quick Prompts ─────────────────────────────────────────────
st.markdown('<div class="sec-label">Quick prompts</div>', unsafe_allow_html=True)
pcols = st.columns(4)
for i, prompt in enumerate(selected["prompts"]):
    with pcols[i % 4]:
        if st.button(f"→ {prompt[:30]}{'…' if len(prompt)>30 else ''}", key=f"p_{i}", use_container_width=True):
            st.session_state.task_text = prompt
            st.rerun()

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Task Input ────────────────────────────────────────────────
st.markdown('<div class="sec-label">Your task</div>', unsafe_allow_html=True)
task_input = st.text_area("task", value=st.session_state.task_text,
    placeholder=f"Describe what you want the {selected_name} agent to do...",
    height=110, label_visibility="collapsed")

uploaded_file = None
paste_text = None

if selected["needs_csv"]:
    st.markdown('<div class="sec-label" style="margin-top:18px;">Upload CSV</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("CSV", type=["csv"], label_visibility="collapsed")
    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} — {uploaded_file.size//1024} KB ready")

if selected["route"] == "SUMMARIZE":
    st.markdown('<div class="sec-label" style="margin-top:18px;">Paste your text</div>', unsafe_allow_html=True)
    paste_text = st.text_area("paste", placeholder="Paste article, document, or any text here...", height=150, label_visibility="collapsed")

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Run Button ────────────────────────────────────────────────
run = st.button(f"⚡  Run {selected_name} Agent", use_container_width=True)

# ── Show history output ───────────────────────────────────────
if st.session_state.last_output and not run:
    item = st.session_state.last_output
    st.markdown(f"""
    <div class="output-card">
        <div class="out-meta">
            <span style="font-size:24px">{item['icon']}</span>
            <span class="out-badge">{item['agent']}</span>
            <span class="out-task">{item['task'][:50]}</span>
            <span class="out-time">{item['time']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(item["output"])

# ── Processing ────────────────────────────────────────────────
if run:
    final_task = task_input.strip()
    if selected["route"] == "SUMMARIZE" and paste_text:
        final_task = f"Summarize this: {paste_text[:3000]}"

    if not final_task:
        st.error("✦ Please enter a task or pick a quick prompt above.")
    elif selected["needs_csv"] and not uploaded_file:
        st.error("✦ Please upload a CSV file for the Data Analyst agent.")
    else:
        temp_file_path = None
        if uploaded_file:
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            df = pd.read_csv(uploaded_file)
            df.to_csv(temp_file_path, index=False)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: s1 = st.empty(); s1.markdown('<div class="step-item active">🤔 Understanding task</div>', unsafe_allow_html=True)
        with c2: s2 = st.empty(); s2.markdown('<div class="step-item">⚙️ Agent processing</div>', unsafe_allow_html=True)
        with c3: s3 = st.empty(); s3.markdown('<div class="step-item">✨ Preparing output</div>', unsafe_allow_html=True)

        try:
            try: api_key = st.secrets["GROQ_API_KEY"]
            except: api_key = os.environ.get("GROQ_API_KEY")

            from langchain_groq import ChatGroq
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)

            s1.markdown('<div class="step-item done">✅ Task understood</div>', unsafe_allow_html=True)
            s2.markdown('<div class="step-item active">⚙️ Agent processing...</div>', unsafe_allow_html=True)

            output = ""
            route = selected["route"]

            if route == "EMAIL":
                r = llm.invoke(f"Write a professional email for: {final_task}\n\nFormat:\n**Subject:** [subject]\n\n**Email:**\n[body under 180 words, warm and specific]")
                output = r.content
            elif route == "SEO":
                r = llm.invoke(f"Write SEO content for: {final_task}\n\nInclude: **Title**, **Meta Description** (155 chars), **Full Article** (750 words with H2s), **Keywords**, **CTA**")
                output = r.content
            elif route == "SUMMARIZE":
                r = llm.invoke(f"{final_task}\n\nFormat:\n**⚡ TL;DR:** (2 sentences)\n\n**🔑 Key Points:**\n(8 bullets)\n\n**📊 Important Facts:**\n(numbers/dates)\n\n**💡 Takeaway:**\n(1 paragraph)")
                output = r.content
            else:
                from orchestrator import build_orchestrator
                result = build_orchestrator().invoke({"user_task": final_task, "route": "", "file_path": temp_file_path, "final_output": "", "error": None})
                output = result["final_output"]

            s2.markdown('<div class="step-item done">✅ Agent completed</div>', unsafe_allow_html=True)
            s3.markdown('<div class="step-item done">✅ Output ready</div>', unsafe_allow_html=True)

            hist = {"icon": selected["icon"], "agent": selected_name, "task": final_task, "output": output, "time": datetime.now().strftime("%H:%M")}
            st.session_state.history.append(hist)
            st.session_state.last_output = hist

            st.markdown(f"""
            <div class="output-card">
                <div class="out-meta">
                    <span style="font-size:24px">{selected['icon']}</span>
                    <span class="out-badge">{selected_name}</span>
                    <span class="out-task">{final_task[:48]}{'…' if len(final_task)>48 else ''}</span>
                    <span class="out-time">{datetime.now().strftime("%H:%M")}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(output)
            st.download_button("⬇️ Download Output", data=output,
                file_name=f"agentiq_{route.lower()}_{datetime.now().strftime('%H%M')}.txt", mime="text/plain")

        except Exception as e:
            s1.empty(); s2.empty(); s3.empty()
            st.error(f"Error: {str(e)}")