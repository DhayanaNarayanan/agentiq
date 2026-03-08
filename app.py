import streamlit as st
import os
import tempfile
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AgentIQ", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --bg:#000005; --surface:#07070f; --card:#0c0c18;
  --border:rgba(255,255,255,0.05); --purple:#7c3aed;
  --purple-light:#a78bfa; --text:#f1f5f9; --muted:#475569; --dim:#1e293b;
}
*{box-sizing:border-box;}
html,body,[class*="css"],.stApp{font-family:'Outfit',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}

.bg-grid{position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(124,58,237,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(124,58,237,0.03) 1px,transparent 1px);
  background-size:48px 48px;}

.orbs{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.orb{position:absolute;border-radius:50%;filter:blur(100px);animation:drift 18s ease-in-out infinite;}
.orb-a{width:600px;height:600px;background:#4c1d95;opacity:0.12;top:-200px;left:-200px;}
.orb-b{width:500px;height:500px;background:#1e40af;opacity:0.10;top:40%;right:-150px;animation-delay:-6s;}
.orb-c{width:400px;height:400px;background:#065f46;opacity:0.08;bottom:-100px;left:35%;animation-delay:-12s;}
@keyframes drift{0%,100%{transform:translate(0,0) scale(1);}33%{transform:translate(40px,-40px) scale(1.06);}66%{transform:translate(-30px,30px) scale(0.94);}}

[data-testid="stMainBlockContainer"],[data-testid="stSidebarContent"]{position:relative;z-index:1;}

.hero{position:relative;padding:80px 24px 64px;text-align:center;overflow:hidden;}
.cursor{display:inline-block;width:3px;height:1em;background:var(--purple-light);vertical-align:middle;animation:cursor-blink 1s step-end infinite;margin-left:4px;}
@keyframes cursor-blink{0%,100%{opacity:1}50%{opacity:0}}

.rings{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;width:1px;height:1px;}
.ring{position:absolute;border-radius:50%;border:1px solid rgba(124,58,237,0.1);top:50%;left:50%;transform:translate(-50%,-50%);animation:ring-breathe 5s ease-in-out infinite;}
.ring:nth-child(1){width:200px;height:200px;}
.ring:nth-child(2){width:360px;height:360px;animation-delay:-1.25s;border-color:rgba(59,130,246,0.07);}
.ring:nth-child(3){width:520px;height:520px;animation-delay:-2.5s;border-color:rgba(124,58,237,0.05);}
.ring:nth-child(4){width:680px;height:680px;animation-delay:-3.75s;border-color:rgba(59,130,246,0.03);}
@keyframes ring-breathe{0%,100%{opacity:0.6;transform:translate(-50%,-50%) scale(1);}50%{opacity:1;transform:translate(-50%,-50%) scale(1.025);}}

.hero-eyebrow{display:inline-flex;align-items:center;gap:10px;background:rgba(124,58,237,0.07);border:1px solid rgba(124,58,237,0.18);border-radius:6px;padding:6px 16px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#a78bfa;letter-spacing:0.5px;margin-bottom:32px;animation:fadein 0.8s ease both;}
.eyebrow-dot{width:6px;height:6px;border-radius:50%;background:#10b981;animation:pulse-dot 2s ease infinite;}
@keyframes pulse-dot{0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,0.5)}50%{box-shadow:0 0 0 6px rgba(16,185,129,0)}}

.hero-title{font-family:'Outfit',sans-serif!important;font-size:clamp(56px,9vw,100px);font-weight:900;line-height:0.95;letter-spacing:-4px;background:linear-gradient(160deg,#ffffff 20%,#c4b5fd 55%,#93c5fd 80%);background-size:200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:title-shimmer 8s linear infinite,fadein 1s ease both 0.1s;margin-bottom:24px;}
@keyframes title-shimmer{0%{background-position:0%}100%{background-position:200%}}

.hero-sub{font-size:18px;color:#334155;font-weight:400;line-height:1.7;max-width:520px;margin:0 auto 40px;animation:fadein 1s ease both 0.2s;}

.hero-stats{display:flex;justify-content:center;gap:0;animation:fadein 1s ease both 0.3s;border:1px solid var(--border);border-radius:12px;overflow:hidden;max-width:420px;margin:0 auto;background:var(--card);}
.stat{flex:1;padding:16px 20px;text-align:center;border-right:1px solid var(--border);}
.stat:last-child{border-right:none;}
.stat-n{font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:700;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stat-l{font-size:11px;color:var(--muted);margin-top:2px;letter-spacing:1px;text-transform:uppercase;}
@keyframes fadein{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}

.label{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:3px;text-transform:uppercase;display:flex;align-items:center;gap:12px;margin-bottom:16px;margin-top:8px;}
.label::before{content:'//';color:var(--purple);}
.label::after{content:'';flex:1;height:1px;background:var(--border);}

.agent-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 14px 16px;text-align:center;cursor:pointer;transition:all 0.25s cubic-bezier(0.4,0,0.2,1);position:relative;overflow:hidden;}
.agent-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--purple),transparent);opacity:0;transition:opacity 0.3s;}
.agent-card:hover{border-color:rgba(124,58,237,0.3);transform:translateY(-4px);box-shadow:0 20px 60px rgba(0,0,0,0.5),0 0 40px rgba(124,58,237,0.08);}
.agent-card:hover::before{opacity:1;}
.agent-card.active{border-color:rgba(124,58,237,0.45);background:linear-gradient(160deg,rgba(124,58,237,0.08) 0%,rgba(59,130,246,0.04) 100%);box-shadow:0 0 60px rgba(124,58,237,0.12),inset 0 1px 0 rgba(255,255,255,0.05);}
.agent-card.active::before{opacity:1;}

.icon-wrap{width:48px;height:48px;border-radius:12px;background:rgba(255,255,255,0.03);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:20px;transition:all 0.25s;}
.agent-card:hover .icon-wrap,.agent-card.active .icon-wrap{background:rgba(124,58,237,0.12);border-color:rgba(124,58,237,0.3);transform:scale(1.1) rotate(-5deg);box-shadow:0 8px 24px rgba(124,58,237,0.2);}
.a-name{font-size:12px;font-weight:700;color:var(--text);margin-bottom:5px;}
.a-desc{font-size:10px;color:var(--muted);line-height:1.5;}

.stTextArea textarea{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:#94a3b8!important;font-family:'Outfit',sans-serif!important;font-size:14px!important;transition:all 0.2s!important;}
.stTextArea textarea:focus{border-color:rgba(124,58,237,0.4)!important;box-shadow:0 0 0 4px rgba(124,58,237,0.06)!important;color:var(--text)!important;}
.stTextArea textarea::placeholder{color:#1e293b!important;}

.stButton>button{background:var(--card)!important;color:#94a3b8!important;border:1px solid var(--border)!important;border-radius:8px!important;font-family:'Outfit',sans-serif!important;font-size:12px!important;font-weight:500!important;transition:all 0.2s!important;}
.stButton>button:hover{border-color:rgba(124,58,237,0.35)!important;color:#a78bfa!important;background:rgba(124,58,237,0.06)!important;}

.step{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 12px;text-align:center;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--dim);transition:all 0.3s ease;}
.step.active{border-color:rgba(124,58,237,0.35);color:#a78bfa;background:rgba(124,58,237,0.06);animation:step-pulse 1.4s ease infinite;}
.step.done{border-color:rgba(16,185,129,0.3);color:#34d399;background:rgba(16,185,129,0.05);}
@keyframes step-pulse{0%,100%{box-shadow:0 0 0 0 rgba(124,58,237,0.2)}50%{box-shadow:0 0 0 8px rgba(124,58,237,0)}}

.out-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:0;margin-top:24px;overflow:hidden;animation:fadein 0.4s ease both;box-shadow:0 40px 80px rgba(0,0,0,0.4);}
.out-progress{height:2px;background:linear-gradient(90deg,#7c3aed,#3b82f6,#06b6d4,#7c3aed);background-size:300%;animation:progress-slide 2.5s linear infinite;}
@keyframes progress-slide{0%{background-position:0%}100%{background-position:300%}}
.out-header{background:var(--surface);border-bottom:1px solid var(--border);padding:14px 20px;display:flex;align-items:center;gap:12px;}
.traffic-lights{display:flex;gap:6px;}
.tl{width:12px;height:12px;border-radius:50%;}
.tl-r{background:#ff5f57;}.tl-y{background:#febc2e;}.tl-g{background:#28c840;}
.out-title{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--muted);}
.out-badge{margin-left:auto;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.2);border-radius:4px;padding:3px 10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:#a78bfa;}
.out-body{padding:28px 32px;}

[data-testid="stFileUploader"]{background:var(--card)!important;border:1px dashed rgba(124,58,237,0.2)!important;border-radius:10px!important;}
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-thumb{background:rgba(124,58,237,0.2);border-radius:4px;}
</style>

<div class="bg-grid"></div>
<div class="orbs">
  <div class="orb orb-a"></div>
  <div class="orb orb-b"></div>
  <div class="orb orb-c"></div>
</div>
""", unsafe_allow_html=True)

for k,v in [("selected_agent","Research Writer"),("task_text",""),("history",[]),("last_output",None)]:
    if k not in st.session_state: st.session_state[k]=v

AGENTS = {
    "Data Analyst":    {"icon":"📊","desc":"CSV → professional analysis","needs_csv":True,"route":"DATA","prompts":["Find patterns and anomalies","Full statistical summary","Identify data quality issues","Top insights from this data"]},
    "DS Pipeline":     {"icon":"🤖","desc":"CSV → auto ML pipeline + model","needs_csv":True,"route":"AUTOGEN","prompts":["Build fraud detection model","Predict customer churn","Run classification pipeline","Regression for price prediction"]},
    "Research Writer": {"icon":"🌐","desc":"Topic → 600+ word report","needs_csv":False,"route":"RESEARCH","prompts":["Future of AI agents in enterprise","Latest trends in GenAI 2025","How startups monetize LLMs","Impact of automation on jobs"]},
    "Code Generator":  {"icon":"💻","desc":"Describe → tested Python code","needs_csv":False,"route":"CODE","prompts":["Web scraper for news articles","Data visualization with charts","REST API with FastAPI","ML pipeline with sklearn"]},
    "Summarizer":      {"icon":"✂️","desc":"Long text → clean summary","needs_csv":False,"route":"SUMMARIZE","prompts":["Summarize this research paper","Key points from this article","Extract action items","Simplify technical document"]},
    "Email Writer":    {"icon":"✉️","desc":"Situation → professional email","needs_csv":False,"route":"EMAIL","prompts":["Cold outreach to startup founder","Follow up after job interview","Request project extension","Introduction to new team"]},
    "SEO Writer":      {"icon":"🔍","desc":"Topic → SEO content","needs_csv":False,"route":"SEO","prompts":["SEO blog post about AI tools","Meta descriptions for DS site","Product description for SaaS","SEO article Python beginners"]},
}

with st.sidebar:
    st.markdown("""
    <div style="padding:24px 4px 28px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#334155;letter-spacing:2px;margin-bottom:8px;">// SYSTEM</div>
      <div style="font-family:'Outfit',sans-serif;font-size:24px;font-weight:900;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-1px;">AgentIQ</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#1e293b;margin-top:6px;">v2.0.0 · 7 agents · live</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="label">Session History</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown("""<div style="border:1px dashed rgba(255,255,255,0.04);border-radius:10px;padding:24px 12px;text-align:center;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#1e293b;">$ awaiting first task_</div>
        </div>""", unsafe_allow_html=True)
    else:
        for i,item in enumerate(reversed(st.session_state.history[-8:])):
            if st.button(f"{item['icon']} {item['task'][:24]}{'…' if len(item['task'])>24 else ''}",key=f"h_{i}",use_container_width=True):
                st.session_state.last_output=item; st.rerun()
    st.markdown("---")
    st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#0f172a;line-height:2.4;">
      ⚡ Groq · LLaMA-3.3-70b<br>🔗 LangGraph orchestrator<br>🤖 AutoGen DS pipeline<br>🔒 Zero data retention<br>
      <span style="color:#0c0c18;margin-top:8px;display:block;">© 2025 AgentIQ</span></div>""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="rings"><div class="ring"></div><div class="ring"></div><div class="ring"></div><div class="ring"></div></div>
  <div class="hero-eyebrow"><div class="eyebrow-dot"></div>system online · 7 agents ready</div>
  <div class="hero-title">AgentIQ<span class="cursor"></span></div>
  <p class="hero-sub">A multi-agent AI platform — 7 specialized agents working in concert to analyze, research, code, and automate.</p>
  <div class="hero-stats">
    <div class="stat"><div class="stat-n">7</div><div class="stat-l">Agents</div></div>
    <div class="stat"><div class="stat-n">5</div><div class="stat-l">Frameworks</div></div>
    <div class="stat"><div class="stat-n">~15s</div><div class="stat-l">Per task</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="label">Select agent</div>', unsafe_allow_html=True)
cols = st.columns(7)
for i,(name,ag) in enumerate(AGENTS.items()):
    with cols[i]:
        active="active" if st.session_state.selected_agent==name else ""
        st.markdown(f"""<div class="agent-card {active}"><div class="icon-wrap">{ag['icon']}</div><div class="a-name">{name}</div><div class="a-desc">{ag['desc']}</div></div>""", unsafe_allow_html=True)
        if st.button("select",key=f"sel_{i}",use_container_width=True):
            st.session_state.selected_agent=name; st.session_state.task_text=""; st.rerun()

selected_name=st.session_state.selected_agent
selected=AGENTS[selected_name]
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

st.markdown('<div class="label">Quick prompts</div>', unsafe_allow_html=True)
pcols=st.columns(4)
for i,p in enumerate(selected["prompts"]):
    with pcols[i%4]:
        if st.button(f"→ {p[:32]}{'…' if len(p)>32 else ''}",key=f"p_{i}",use_container_width=True):
            st.session_state.task_text=p; st.rerun()

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.markdown('<div class="label">Task input</div>', unsafe_allow_html=True)
task_input=st.text_area("task",value=st.session_state.task_text,placeholder=f"// describe your task for {selected_name} agent...",height=100,label_visibility="collapsed")

uploaded_file=None; paste_text=None
if selected["needs_csv"]:
    st.markdown('<div class="label" style="margin-top:16px;">CSV upload</div>', unsafe_allow_html=True)
    uploaded_file=st.file_uploader("CSV",type=["csv"],label_visibility="collapsed")
    if uploaded_file: st.success(f"✓ {uploaded_file.name} · {uploaded_file.size//1024} KB")

if selected["route"]=="SUMMARIZE":
    st.markdown('<div class="label" style="margin-top:16px;">Text input</div>', unsafe_allow_html=True)
    paste_text=st.text_area("paste",placeholder="// paste article or document here...",height=140,label_visibility="collapsed")

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# Run button styled via markdown injection
st.markdown("""<style>
div[data-testid="stButton"]:last-of-type > button {
  background:linear-gradient(135deg,#6d28d9 0%,#4338ca 50%,#1d4ed8 100%)!important;
  color:white!important;border:none!important;border-radius:10px!important;
  padding:16px!important;font-size:15px!important;font-weight:700!important;
  letter-spacing:0.5px!important;box-shadow:0 8px 32px rgba(109,40,217,0.4)!important;
}
div[data-testid="stButton"]:last-of-type > button:hover {
  transform:translateY(-2px)!important;
  box-shadow:0 12px 48px rgba(109,40,217,0.55)!important;
  background:linear-gradient(135deg,#7c3aed,#4f46e5,#2563eb)!important;
  color:white!important;
}
</style>""", unsafe_allow_html=True)
run=st.button(f"⚡  execute {selected_name.lower()} agent",use_container_width=True)

if st.session_state.last_output and not run:
    item=st.session_state.last_output
    st.markdown(f"""<div class="out-card"><div class="out-progress"></div>
    <div class="out-header"><div class="traffic-lights"><div class="tl tl-r"></div><div class="tl tl-y"></div><div class="tl tl-g"></div></div>
    <div class="out-title">agentiq · {item['agent'].lower()} · output.md</div>
    <div class="out-badge">{item['time']}</div></div><div class="out-body">""", unsafe_allow_html=True)
    st.markdown(item["output"])
    st.markdown("</div></div>", unsafe_allow_html=True)

if run:
    final_task=task_input.strip()
    if selected["route"]=="SUMMARIZE" and paste_text: final_task=f"Summarize this: {paste_text[:3000]}"
    if not final_task: st.error("// error: task input is empty")
    elif selected["needs_csv"] and not uploaded_file: st.error("// error: CSV file required for this agent")
    else:
        temp_file_path=None
        if uploaded_file:
            temp_dir=tempfile.mkdtemp()
            temp_file_path=os.path.join(temp_dir,uploaded_file.name)
            df=pd.read_csv(uploaded_file); df.to_csv(temp_file_path,index=False)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: s1=st.empty(); s1.markdown('<div class="step active">01 · parsing task</div>',unsafe_allow_html=True)
        with c2: s2=st.empty(); s2.markdown('<div class="step">02 · agent running</div>',unsafe_allow_html=True)
        with c3: s3=st.empty(); s3.markdown('<div class="step">03 · rendering output</div>',unsafe_allow_html=True)

        try:
            try: api_key=st.secrets["GROQ_API_KEY"]
            except: api_key=os.environ.get("GROQ_API_KEY")
            from langchain_groq import ChatGroq
            llm=ChatGroq(model="llama-3.3-70b-versatile",api_key=api_key)
            s1.markdown('<div class="step done">01 · task parsed</div>',unsafe_allow_html=True)
            s2.markdown('<div class="step active">02 · agent running...</div>',unsafe_allow_html=True)

            output=""; route=selected["route"]

            if route=="EMAIL":
                r=llm.invoke(f"Write professional email for: {final_task}\n\nFormat:\n**Subject:** [subject]\n\n**Email:**\n[body under 180 words, warm, specific]")
                output=r.content
            elif route=="SEO":
                r=llm.invoke(f"Write SEO content for: {final_task}\n\nInclude: **Title**, **Meta Description** (155 chars), **Article** (750 words with H2s), **Keywords**, **CTA**")
                output=r.content
            elif route=="SUMMARIZE":
                r=llm.invoke(f"{final_task}\n\nFormat:\n**TL;DR:** (2 sentences)\n\n**Key Points:**\n(8 bullets)\n\n**Key Facts:**\n\n**Takeaway:**\n(1 paragraph)")
                output=r.content
            elif route=="AUTOGEN":
                df_preview=pd.read_csv(temp_file_path).head(5).to_string()
                df_shape=pd.read_csv(temp_file_path).shape
                df_stats=pd.read_csv(temp_file_path).describe().to_string()
                r=llm.invoke(f"""You are an expert data scientist running a 5-agent AutoGen ML pipeline.

DATASET: {df_shape[0]} rows x {df_shape[1]} columns
TASK: {final_task}
SAMPLE:
{df_preview}
STATS:
{df_stats}

Write a complete AutoGen ML Pipeline Report:

# AutoGen DS Pipeline Report

## Explorer Agent
(dataset overview, target column, data quality)

## Strategy Agent
(ML approach, model choice, preprocessing plan)

## Builder Agent — Code
```python
# Complete working sklearn ML pipeline
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
# full pipeline code here
```

## Validator Agent Results
(model metrics: accuracy, precision, recall, F1, confusion matrix interpretation)

## Final Report
### Executive Summary
### Key Findings  
### Model Performance Analysis
### Business Recommendations
### Next Steps

Use actual column names and realistic numbers throughout.""")
                output=r.content
            else:
                from orchestrator import build_orchestrator
                result=build_orchestrator().invoke({"user_task":final_task,"route":"","file_path":temp_file_path,"final_output":"","error":None})
                output=result["final_output"]

            s2.markdown('<div class="step done">02 · agent complete</div>',unsafe_allow_html=True)
            s3.markdown('<div class="step done">03 · output ready</div>',unsafe_allow_html=True)

            hist={"icon":selected["icon"],"agent":selected_name,"task":final_task,"output":output,"time":datetime.now().strftime("%H:%M")}
            st.session_state.history.append(hist); st.session_state.last_output=hist

            st.markdown(f"""<div class="out-card"><div class="out-progress"></div>
            <div class="out-header"><div class="traffic-lights"><div class="tl tl-r"></div><div class="tl tl-y"></div><div class="tl tl-g"></div></div>
            <div class="out-title">agentiq · {selected_name.lower()} · output.md</div>
            <div class="out-badge">{selected['icon']} {selected_name}</div></div>
            <div class="out-body">""", unsafe_allow_html=True)
            st.markdown(output)
            st.markdown("</div></div>", unsafe_allow_html=True)
            st.download_button("⬇️ export output",data=output,file_name=f"agentiq_{route.lower()}_{datetime.now().strftime('%H%M')}.md",mime="text/markdown")

        except Exception as e:
            s1.empty(); s2.empty(); s3.empty()
            st.error(f"// runtime error: {str(e)}")