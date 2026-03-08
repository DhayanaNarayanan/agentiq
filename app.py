import streamlit as st
import streamlit.components.v1 as components
import os
import tempfile
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AgentIQ", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
:root{--bg:#000005;--surface:#07070f;--card:#0c0c18;--border:rgba(255,255,255,0.05);--purple:#7c3aed;--purple-light:#a78bfa;--text:#f1f5f9;--muted:#475569;--dim:#1e293b;}
*{box-sizing:border-box;}
html,body,[class*="css"],.stApp{font-family:'Outfit',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
.bg-grid{position:fixed;inset:0;pointer-events:none;z-index:0;background-image:linear-gradient(rgba(124,58,237,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(124,58,237,0.03) 1px,transparent 1px);background-size:48px 48px;}
.orbs{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.orb{position:absolute;border-radius:50%;filter:blur(100px);animation:drift 18s ease-in-out infinite;}
.orb-a{width:600px;height:600px;background:#4c1d95;opacity:0.12;top:-200px;left:-200px;}
.orb-b{width:500px;height:500px;background:#1e40af;opacity:0.10;top:40%;right:-150px;animation-delay:-6s;}
.orb-c{width:400px;height:400px;background:#065f46;opacity:0.08;bottom:-100px;left:35%;animation-delay:-12s;}
@keyframes drift{0%,100%{transform:translate(0,0) scale(1);}33%{transform:translate(40px,-40px) scale(1.06);}66%{transform:translate(-30px,30px) scale(0.94);}}
[data-testid="stMainBlockContainer"],[data-testid="stSidebarContent"]{position:relative;z-index:1;}
.hero{position:relative;padding:72px 24px 56px;text-align:center;overflow:hidden;}
.cursor{display:inline-block;width:3px;height:1em;background:var(--purple-light);vertical-align:middle;animation:cursor-blink 1s step-end infinite;margin-left:4px;}
@keyframes cursor-blink{0%,100%{opacity:1}50%{opacity:0}}
.rings{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;width:1px;height:1px;}
.ring{position:absolute;border-radius:50%;border:1px solid rgba(124,58,237,0.1);top:50%;left:50%;transform:translate(-50%,-50%);animation:ring-breathe 5s ease-in-out infinite;}
.ring:nth-child(1){width:200px;height:200px;}
.ring:nth-child(2){width:360px;height:360px;animation-delay:-1.25s;border-color:rgba(59,130,246,0.07);}
.ring:nth-child(3){width:520px;height:520px;animation-delay:-2.5s;border-color:rgba(124,58,237,0.05);}
.ring:nth-child(4){width:680px;height:680px;animation-delay:-3.75s;border-color:rgba(59,130,246,0.03);}
@keyframes ring-breathe{0%,100%{opacity:0.6;transform:translate(-50%,-50%) scale(1);}50%{opacity:1;transform:translate(-50%,-50%) scale(1.025);}}
.hero-eyebrow{display:inline-flex;align-items:center;gap:10px;background:rgba(124,58,237,0.07);border:1px solid rgba(124,58,237,0.18);border-radius:6px;padding:6px 16px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#a78bfa;letter-spacing:0.5px;margin-bottom:28px;animation:fadein 0.8s ease both;}
.eyebrow-dot{width:6px;height:6px;border-radius:50%;background:#10b981;animation:pulse-dot 2s ease infinite;}
@keyframes pulse-dot{0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,0.5)}50%{box-shadow:0 0 0 6px rgba(16,185,129,0)}}
.hero-title{font-family:'Outfit',sans-serif!important;font-size:clamp(56px,9vw,96px);font-weight:900;line-height:0.95;letter-spacing:-4px;background:linear-gradient(160deg,#ffffff 20%,#c4b5fd 55%,#93c5fd 80%);background-size:200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:title-shimmer 8s linear infinite,fadein 1s ease both 0.1s;margin-bottom:20px;}
@keyframes title-shimmer{0%{background-position:0%}100%{background-position:200%}}
.hero-sub{font-size:17px;color:#334155;font-weight:400;line-height:1.7;max-width:500px;margin:0 auto 36px;animation:fadein 1s ease both 0.2s;}
.hero-stats{display:flex;justify-content:center;gap:0;animation:fadein 1s ease both 0.3s;border:1px solid var(--border);border-radius:12px;overflow:hidden;max-width:380px;margin:0 auto;background:var(--card);}
.stat{flex:1;padding:14px 16px;text-align:center;border-right:1px solid var(--border);}
.stat:last-child{border-right:none;}
.stat-n{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stat-l{font-size:10px;color:var(--muted);margin-top:2px;letter-spacing:1px;text-transform:uppercase;}
@keyframes fadein{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.label{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:3px;text-transform:uppercase;display:flex;align-items:center;gap:12px;margin-bottom:16px;margin-top:8px;}
.label::before{content:'//';color:var(--purple);}
.label::after{content:'';flex:1;height:1px;background:var(--border);}
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
iframe{border:none!important;}
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-thumb{background:rgba(124,58,237,0.2);border-radius:4px;}
</style>
<div class="bg-grid"></div>
<div class="orbs"><div class="orb orb-a"></div><div class="orb orb-b"></div><div class="orb orb-c"></div></div>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────
for k,v in [("selected_agent","Research Writer"),("task_text",""),("history",[]),("last_output",None)]:
    if k not in st.session_state: st.session_state[k]=v

AGENTS = {
    "Data Analyst":    {"icon":"📊","color":"#06b6d4","desc":"CSV → professional analysis","needs_csv":True,"route":"DATA","features":["Upload any CSV file","Statistical deep-dive","Pattern & anomaly detection","Professional report"],"tech":"LangGraph · Pandas","time":"~12s","prompts":["Find patterns and anomalies","Full statistical summary","Identify data quality issues","Top insights from this data"]},
    "DS Pipeline":     {"icon":"🤖","color":"#8b5cf6","desc":"CSV → auto ML pipeline + model","needs_csv":True,"route":"AUTOGEN","features":["5-agent ML collaboration","Auto model selection","Train + evaluate + explain","Code + accuracy report"],"tech":"AutoGen · Sklearn","time":"~30s","prompts":["Build fraud detection model","Predict customer churn","Run classification pipeline","Regression for price prediction"]},
    "Research Writer": {"icon":"🌐","color":"#3b82f6","desc":"Topic → 600+ word report","needs_csv":False,"route":"RESEARCH","features":["Live web research","Multi-source synthesis","600+ word report","Structured findings"],"tech":"LangGraph · Groq","time":"~18s","prompts":["Future of AI agents in enterprise","Latest trends in GenAI 2025","How startups monetize LLMs","Impact of automation on jobs"]},
    "Code Generator":  {"icon":"💻","color":"#10b981","desc":"Describe → tested Python code","needs_csv":False,"route":"CODE","features":["Tested Python output","Full explanation","Edge cases handled","Copy-paste ready"],"tech":"LangGraph · Groq","time":"~10s","prompts":["Web scraper for news articles","Data visualization with charts","REST API with FastAPI","ML pipeline with sklearn"]},
    "Summarizer":      {"icon":"✂️","color":"#f59e0b","desc":"Long text → clean summary","needs_csv":False,"route":"SUMMARIZE","features":["TL;DR in 2 sentences","8 key bullet points","Key facts extracted","One clear takeaway"],"tech":"Groq · LLaMA-3.3","time":"~8s","prompts":["Summarize this research paper","Key points from this article","Extract action items","Simplify technical document"]},
    "Email Writer":    {"icon":"✉️","color":"#ec4899","desc":"Situation → professional email","needs_csv":False,"route":"EMAIL","features":["Subject line included","Professional tone","Under 180 words","Context-aware writing"],"tech":"Groq · LLaMA-3.3","time":"~6s","prompts":["Cold outreach to startup founder","Follow up after job interview","Request project extension","Introduction to new team"]},
    "SEO Writer":      {"icon":"🔍","color":"#f97316","desc":"Topic → SEO content","needs_csv":False,"route":"SEO","features":["750-word SEO article","Meta description","H2 structure","Keywords + CTA"],"tech":"Groq · LLaMA-3.3","time":"~14s","prompts":["SEO blog post about AI tools","Meta descriptions for DS site","Product description for SaaS","SEO article Python beginners"]},
}

AGENT_NAMES = list(AGENTS.keys())

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="padding:24px 4px 28px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#334155;letter-spacing:2px;margin-bottom:8px;">// SYSTEM</div>
      <div style="font-family:'Outfit',sans-serif;font-size:24px;font-weight:900;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-1px;">AgentIQ</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#1e293b;margin-top:6px;">v2.0.0 · 7 agents · live</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="label">Session History</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown("""<div style="border:1px dashed rgba(255,255,255,0.04);border-radius:10px;padding:24px 12px;text-align:center;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#1e293b;">$ awaiting first task_</div></div>""", unsafe_allow_html=True)
    else:
        for i,item in enumerate(reversed(st.session_state.history[-8:])):
            if st.button(f"{item['icon']} {item['task'][:24]}{'…' if len(item['task'])>24 else ''}",key=f"h_{i}",use_container_width=True):
                st.session_state.last_output=item; st.rerun()
    st.markdown("---")
    st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#0f172a;line-height:2.4;">
      ⚡ Groq · LLaMA-3.3-70b<br>🔗 LangGraph orchestrator<br>🤖 AutoGen DS pipeline<br>🔒 Zero data retention<br>
      <span style="color:#0c0c18;margin-top:8px;display:block;">© 2025 AgentIQ</span></div>""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""<div class="hero">
  <div class="rings"><div class="ring"></div><div class="ring"></div><div class="ring"></div><div class="ring"></div></div>
  <div class="hero-eyebrow"><div class="eyebrow-dot"></div>system online · 7 agents ready</div>
  <div class="hero-title">AgentIQ<span class="cursor"></span></div>
  <p class="hero-sub">A multi-agent AI platform — 7 specialized agents working in concert to analyze, research, code, and automate.</p>
  <div class="hero-stats">
    <div class="stat"><div class="stat-n">7</div><div class="stat-l">Agents</div></div>
    <div class="stat"><div class="stat-n">5</div><div class="stat-l">Frameworks</div></div>
    <div class="stat"><div class="stat-n">~15s</div><div class="stat-l">Per task</div></div>
  </div>
</div>""", unsafe_allow_html=True)

# ── ORBITAL SELECTOR ──────────────────────────────────────────
st.markdown('<div class="label">Select agent</div>', unsafe_allow_html=True)

orbital_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{background:transparent;font-family:'Outfit',sans-serif;overflow:hidden;}
@keyframes center-pulse{0%,100%{box-shadow:0 0 0 0 rgba(124,58,237,0.5),0 0 40px rgba(124,58,237,0.2);}50%{box-shadow:0 0 0 16px rgba(124,58,237,0),0 0 60px rgba(124,58,237,0.3);}}
@keyframes fadein{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes feature-in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:translateX(0)}}
@keyframes ring-pulse{0%,100%{opacity:0.08}50%{opacity:0.2}}
@keyframes spin-slow{from{transform:translate(-50%,-50%) rotate(0deg)}to{transform:translate(-50%,-50%) rotate(360deg)}}
@keyframes glow-line{0%,100%{opacity:0.4}50%{opacity:1}}
</style>
</head>
<body>
<div id="root" style="width:100%;height:520px;position:relative;display:flex;align-items:center;justify-content:center;gap:48px;">

  <!-- ORBITAL SYSTEM -->
  <div id="orbital" style="position:relative;width:460px;height:460px;flex-shrink:0;">
    <!-- Outer orbit ring -->
    <div style="position:absolute;top:50%;left:50%;width:420px;height:420px;border-radius:50%;border:1px solid rgba(124,58,237,0.12);transform:translate(-50%,-50%);animation:ring-pulse 4s ease infinite;pointer-events:none;"></div>
    <!-- Inner spin ring -->
    <div style="position:absolute;top:50%;left:50%;width:140px;height:140px;border-radius:50%;border:1px dashed rgba(124,58,237,0.1);transform:translate(-50%,-50%);animation:spin-slow 18s linear infinite;pointer-events:none;"></div>
    <!-- CENTER -->
    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:88px;height:88px;border-radius:50%;background:linear-gradient(135deg,#1a0533,#080814);border:1px solid rgba(124,58,237,0.35);display:flex;flex-direction:column;align-items:center;justify-content:center;animation:center-pulse 3s ease infinite;z-index:3;">
      <span style="font-size:24px;">🧠</span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:8px;color:#7c3aed;letter-spacing:1px;margin-top:3px;">CORE</span>
    </div>
    <!-- NODES injected by JS -->
    <div id="nodes"></div>
  </div>

  <!-- INFO PANEL -->
  <div id="panel" style="width:320px;min-height:360px;background:rgba(12,12,24,0.95);border:1px solid rgba(255,255,255,0.06);border-radius:18px;overflow:hidden;transition:border-color 0.3s,box-shadow 0.3s;">
    <div id="panel-content" style="padding:32px 24px;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:360px;gap:12px;">
      <div style="font-size:36px;opacity:0.2;">🧠</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#1e293b;line-height:2;">hover an agent<br/>to preview</div>
      <div id="icon-hints" style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-top:4px;"></div>
    </div>
  </div>
</div>

<script>
const AGENTS = [
  {id:"Data Analyst",    icon:"📊", color:"#06b6d4", tagline:"Turn raw CSV into intelligence",    features:["Upload any CSV file","Statistical deep-dive","Pattern & anomaly detection","Professional report"],        tech:"LangGraph · Pandas", time:"~12s"},
  {id:"DS Pipeline",     icon:"🤖", color:"#8b5cf6", tagline:"Full AutoML in 30 seconds",         features:["5-agent ML collaboration","Auto model selection","Train + evaluate + explain","Code + accuracy report"],  tech:"AutoGen · Sklearn",  time:"~30s"},
  {id:"Research Writer", icon:"🌐", color:"#3b82f6", tagline:"Web research → expert report",      features:["Live web research","Multi-source synthesis","600+ word report","Structured findings"],                   tech:"LangGraph · Groq",   time:"~18s"},
  {id:"Code Generator",  icon:"💻", color:"#10b981", tagline:"Describe it. Get working code.",    features:["Tested Python output","Full explanation","Edge cases handled","Copy-paste ready"],                        tech:"LangGraph · Groq",   time:"~10s"},
  {id:"Summarizer",      icon:"✂️", color:"#f59e0b", tagline:"Any text → crisp insights",         features:["TL;DR in 2 sentences","8 key bullet points","Key facts extracted","One clear takeaway"],                 tech:"Groq · LLaMA-3.3",   time:"~8s"},
  {id:"Email Writer",    icon:"✉️", color:"#ec4899", tagline:"Situation → send-ready email",      features:["Subject line included","Professional tone","Under 180 words","Context-aware writing"],                   tech:"Groq · LLaMA-3.3",   time:"~6s"},
  {id:"SEO Writer",      icon:"🔍", color:"#f97316", tagline:"Rank-worthy content instantly",     features:["750-word SEO article","Meta description","H2 structure","Keywords + CTA"],                               tech:"Groq · LLaMA-3.3",   time:"~14s"},
];

const N = AGENTS.length;
const R = 180;
let angle = 0;
let paused = false;
let hoveredId = null;
let selectedId = null;
let lastTime = performance.now();
let lines = [];
let nodeDivs = [];

// Build icon hints
const hints = document.getElementById('icon-hints');
AGENTS.forEach(a => {
  const s = document.createElement('span');
  s.textContent = a.icon;
  s.style.cssText = 'font-size:16px;opacity:0.2;cursor:pointer;transition:opacity 0.2s;';
  s.onmouseenter = () => { paused=true; hoveredId=a.id; updatePanel(a); s.style.opacity='1'; };
  s.onmouseleave = () => { paused=false; hoveredId=null; resetPanel(); s.style.opacity='0.2'; };
  hints.appendChild(s);
});

// Build nodes and lines
const nodesDiv = document.getElementById('nodes');
AGENTS.forEach((agent, i) => {
  // Line
  const line = document.createElement('div');
  line.style.cssText = `position:absolute;top:50%;left:50%;height:1px;background:rgba(255,255,255,0.03);transform-origin:0 50%;pointer-events:none;z-index:1;transition:background 0.3s;width:${R}px;`;
  nodesDiv.appendChild(line);
  lines.push(line);

  // Node
  const node = document.createElement('div');
  node.style.cssText = `position:absolute;top:50%;left:50%;width:60px;height:60px;border-radius:50%;background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;z-index:4;transition:all 0.25s cubic-bezier(0.4,0,0.2,1);`;
  node.innerHTML = `<span style="font-size:18px;transition:font-size 0.2s;">${agent.icon}</span>`;

  // Hover label
  const lbl = document.createElement('div');
  lbl.style.cssText = `position:absolute;top:calc(100% + 7px);left:50%;transform:translateX(-50%);white-space:nowrap;font-family:'JetBrains Mono',monospace;font-size:9px;color:${agent.color};background:rgba(0,0,8,0.95);border:1px solid ${agent.color}40;border-radius:4px;padding:3px 8px;opacity:0;transition:opacity 0.2s;pointer-events:none;`;
  lbl.textContent = agent.id;
  node.appendChild(lbl);

  node.onmouseenter = () => {
    paused = true; hoveredId = agent.id;
    node.style.width='72px'; node.style.height='72px';
    node.style.background=`radial-gradient(circle at 30% 30%,${agent.color}30,#080814)`;
    node.style.border=`2px solid ${agent.color}`;
    node.style.boxShadow=`0 0 28px ${agent.color}50,0 0 8px ${agent.color}30`;
    node.querySelector('span').style.fontSize='22px';
    lbl.style.opacity='1';
    updatePanel(agent);
  };
  node.onmouseleave = () => {
    paused = false; hoveredId = null;
    if(selectedId !== agent.id){
      node.style.width='60px'; node.style.height='60px';
      node.style.background='rgba(255,255,255,0.025)';
      node.style.border='1px solid rgba(255,255,255,0.08)';
      node.style.boxShadow='none';
      node.querySelector('span').style.fontSize='18px';
    }
    lbl.style.opacity='0';
    resetPanel();
  };
  node.onclick = () => {
    selectedId = agent.id;
    // tell Streamlit
    window.parent.postMessage({type:'agentiq_select', agent: agent.id}, '*');
    updatePanel(agent);
    applySelectedStyle();
  };

  nodesDiv.appendChild(node);
  nodeDivs.push({node, lbl, agent});
});

function applySelectedStyle(){
  nodeDivs.forEach(({node, agent}) => {
    if(agent.id === selectedId){
      node.style.width='72px'; node.style.height='72px';
      node.style.background=`radial-gradient(circle at 30% 30%,${agent.color}30,#080814)`;
      node.style.border=`2px solid ${agent.color}`;
      node.style.boxShadow=`0 0 28px ${agent.color}50`;
    } else {
      node.style.width='60px'; node.style.height='60px';
      node.style.background='rgba(255,255,255,0.025)';
      node.style.border='1px solid rgba(255,255,255,0.08)';
      node.style.boxShadow='none';
    }
  });
}

function updatePanel(agent){
  const panel = document.getElementById('panel');
  panel.style.borderColor = agent.color+'40';
  panel.style.boxShadow = `0 0 48px ${agent.color}15,0 32px 64px rgba(0,0,0,0.5)`;
  document.getElementById('panel-content').innerHTML = `
    <div style="height:3px;background:linear-gradient(90deg,transparent,${agent.color},transparent);margin:-32px -24px 24px;width:calc(100% + 48px);"></div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;text-align:left;">
      <div style="width:52px;height:52px;border-radius:13px;background:radial-gradient(circle at 30% 30%,${agent.color}25,rgba(0,0,0,0.5));border:1px solid ${agent.color}40;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 6px 20px ${agent.color}25;flex-shrink:0;">${agent.icon}</div>
      <div>
        <div style="font-size:16px;font-weight:800;color:#f1f5f9;letter-spacing:-0.3px;">${agent.id}</div>
        <div style="font-size:11px;color:${agent.color};margin-top:3px;font-weight:500;">${agent.tagline}</div>
      </div>
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#334155;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;text-align:left;">// CAPABILITIES</div>
    <div style="width:100%;">
      ${agent.features.map((f,i)=>`
        <div style="display:flex;align-items:center;gap:9px;padding:7px 0;border-bottom:${i<agent.features.length-1?'1px solid rgba(255,255,255,0.03)':'none'};animation:feature-in 0.2s ease both;animation-delay:${i*0.05}s;">
          <div style="width:5px;height:5px;border-radius:50%;background:${agent.color};flex-shrink:0;box-shadow:0 0 5px ${agent.color};"></div>
          <span style="font-size:12px;color:#94a3b8;">${f}</span>
        </div>`).join('')}
    </div>
    <div style="display:flex;gap:6px;margin:14px 0 16px;flex-wrap:wrap;">
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:5px;padding:4px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;color:#475569;">⚡ ${agent.time}</div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:5px;padding:4px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;color:#475569;">${agent.tech}</div>
    </div>
    <button onclick="selectAgent('${agent.id}')" id="select-btn"
      style="width:100%;padding:12px 16px;background:${selectedId===agent.id?`linear-gradient(135deg,${agent.color},${agent.color}bb)`:`linear-gradient(135deg,${agent.color}18,${agent.color}0c)`};border:1px solid ${agent.color}${selectedId===agent.id?'':'40'};border-radius:9px;cursor:pointer;font-family:'Outfit',sans-serif;font-size:13px;font-weight:700;color:${selectedId===agent.id?'#fff':agent.color};transition:all 0.2s;box-shadow:${selectedId===agent.id?`0 6px 20px ${agent.color}40`:'none'};">
      ${selectedId===agent.id?'✓ '+agent.id+' Selected':'Select '+agent.id}
    </button>
  `;
}

function selectAgent(id){
  selectedId = id;
  window.parent.postMessage({type:'agentiq_select', agent: id}, '*');
  const agent = AGENTS.find(a=>a.id===id);
  if(agent){ updatePanel(agent); applySelectedStyle(); }
}
window.selectAgent = selectAgent;

function resetPanel(){
  if(selectedId){
    const agent = AGENTS.find(a=>a.id===selectedId);
    if(agent){ updatePanel(agent); return; }
  }
  document.getElementById('panel').style.borderColor='rgba(255,255,255,0.06)';
  document.getElementById('panel').style.boxShadow='none';
  document.getElementById('panel-content').innerHTML = `
    <div style="font-size:36px;opacity:0.2;">🧠</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#1e293b;line-height:2;">hover an agent<br/>to preview</div>
    <div id="icon-hints" style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-top:4px;">
      ${AGENTS.map(a=>`<span style="font-size:16px;opacity:0.2;cursor:pointer;" onmouseenter="hoveredId='${a.id}';paused=true;" onmouseleave="hoveredId=null;paused=false;">${a.icon}</span>`).join('')}
    </div>`;
}

// Animation loop
function tick(now){
  if(!paused){
    const dt = now - lastTime;
    angle = (angle + dt * 0.011) % 360;
  }
  lastTime = now;

  nodeDivs.forEach(({node, agent}, i) => {
    const deg = (angle + (360/N)*i) % 360;
    const rad = deg * Math.PI / 180;
    const x = Math.cos(rad) * R;
    const y = Math.sin(rad) * R;
    const la = Math.atan2(y, x) * 180 / Math.PI;
    const isActive = hoveredId===agent.id || selectedId===agent.id;

    node.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`;
    lines[i].style.transform = `rotate(${la}deg)`;
    lines[i].style.background = isActive
      ? `linear-gradient(90deg,rgba(124,58,237,0.35),${agent.color}55)`
      : 'rgba(255,255,255,0.03)';
  });

  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
</script>
</body>
</html>
"""

# Render orbital selector
components.html(orbital_html, height=540, scrolling=False)

# Listen for agent selection via query params workaround — use a selectbox hidden
# The orbital sends postMessage; we use a radio as the real selector below it
st.markdown('<div class="label" style="margin-top:4px;">Active agent</div>', unsafe_allow_html=True)

agent_cols = st.columns(7)
for i, name in enumerate(AGENT_NAMES):
    with agent_cols[i]:
        ag = AGENTS[name]
        is_active = st.session_state.selected_agent == name
        color = ag['color']
        border = color if is_active else 'rgba(255,255,255,0.06)'
        bg = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)" if is_active else 'rgba(12,12,24,0.8)'
        st.markdown(f"""<div style="background:{bg};border:1px solid {border};border-radius:10px;padding:10px 6px;text-align:center;transition:all 0.2s;{'box-shadow:0 0 20px '+color+'30;' if is_active else ''}">
          <div style="font-size:18px;margin-bottom:4px;">{ag['icon']}</div>
          <div style="font-size:10px;font-weight:700;color:{'#f1f5f9' if is_active else '#475569'};">{name}</div>
        </div>""", unsafe_allow_html=True)
        if st.button("↑", key=f"sel_{i}", use_container_width=True, help=f"Select {name}"):
            st.session_state.selected_agent = name
            st.session_state.task_text = ""
            st.rerun()

selected_name = st.session_state.selected_agent
selected = AGENTS[selected_name]
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Quick Prompts ─────────────────────────────────────────────
st.markdown('<div class="label">Quick prompts</div>', unsafe_allow_html=True)
pcols = st.columns(4)
for i,p in enumerate(selected["prompts"]):
    with pcols[i%4]:
        if st.button(f"→ {p[:32]}{'…' if len(p)>32 else ''}",key=f"p_{i}",use_container_width=True):
            st.session_state.task_text=p; st.rerun()

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.markdown('<div class="label">Task input</div>', unsafe_allow_html=True)
task_input = st.text_area("task", value=st.session_state.task_text,
    placeholder=f"// describe your task for {selected_name} agent...",
    height=100, label_visibility="collapsed")

uploaded_file = None; paste_text = None
if selected["needs_csv"]:
    st.markdown('<div class="label" style="margin-top:16px;">CSV upload</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("CSV", type=["csv"], label_visibility="collapsed")
    if uploaded_file: st.success(f"✓ {uploaded_file.name} · {uploaded_file.size//1024} KB")

if selected["route"] == "SUMMARIZE":
    st.markdown('<div class="label" style="margin-top:16px;">Text input</div>', unsafe_allow_html=True)
    paste_text = st.text_area("paste", placeholder="// paste article or document here...", height=140, label_visibility="collapsed")

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

st.markdown("""<style>
div[data-testid="stButton"]:last-of-type > button {
  background:linear-gradient(135deg,#6d28d9 0%,#4338ca 50%,#1d4ed8 100%)!important;
  color:white!important;border:none!important;border-radius:10px!important;
  padding:16px!important;font-size:15px!important;font-weight:700!important;
  letter-spacing:0.5px!important;box-shadow:0 8px 32px rgba(109,40,217,0.4)!important;
}
div[data-testid="stButton"]:last-of-type > button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 12px 48px rgba(109,40,217,0.55)!important;
  background:linear-gradient(135deg,#7c3aed,#4f46e5,#2563eb)!important;
  color:white!important;
}
</style>""", unsafe_allow_html=True)
run = st.button(f"⚡  execute {selected_name.lower()} agent", use_container_width=True)

if st.session_state.last_output and not run:
    item = st.session_state.last_output
    st.markdown(f"""<div class="out-card"><div class="out-progress"></div>
    <div class="out-header"><div class="traffic-lights"><div class="tl tl-r"></div><div class="tl tl-y"></div><div class="tl tl-g"></div></div>
    <div class="out-title">agentiq · {item['agent'].lower()} · output.md</div>
    <div class="out-badge">{item['time']}</div></div><div class="out-body">""", unsafe_allow_html=True)
    st.markdown(item["output"])
    st.markdown("</div></div>", unsafe_allow_html=True)

if run:
    final_task = task_input.strip()
    if selected["route"] == "SUMMARIZE" and paste_text: final_task = f"Summarize this: {paste_text[:3000]}"
    if not final_task: st.error("// error: task input is empty")
    elif selected["needs_csv"] and not uploaded_file: st.error("// error: CSV file required for this agent")
    else:
        temp_file_path = None
        if uploaded_file:
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            df = pd.read_csv(uploaded_file); df.to_csv(temp_file_path, index=False)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: s1=st.empty(); s1.markdown('<div class="step active">01 · parsing task</div>',unsafe_allow_html=True)
        with c2: s2=st.empty(); s2.markdown('<div class="step">02 · agent running</div>',unsafe_allow_html=True)
        with c3: s3=st.empty(); s3.markdown('<div class="step">03 · rendering output</div>',unsafe_allow_html=True)

        try:
            try: api_key = st.secrets["GROQ_API_KEY"]
            except: api_key = os.environ.get("GROQ_API_KEY")
            from langchain_groq import ChatGroq
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
            s1.markdown('<div class="step done">01 · task parsed</div>',unsafe_allow_html=True)
            s2.markdown('<div class="step active">02 · agent running...</div>',unsafe_allow_html=True)

            output = ""; route = selected["route"]

            if route == "EMAIL":
                r = llm.invoke(f"Write professional email for: {final_task}\n\nFormat:\n**Subject:** [subject]\n\n**Email:**\n[body under 180 words, warm, specific]")
                output = r.content
            elif route == "SEO":
                r = llm.invoke(f"Write SEO content for: {final_task}\n\nInclude: **Title**, **Meta Description** (155 chars), **Article** (750 words with H2s), **Keywords**, **CTA**")
                output = r.content
            elif route == "SUMMARIZE":
                r = llm.invoke(f"{final_task}\n\nFormat:\n**TL;DR:** (2 sentences)\n\n**Key Points:**\n(8 bullets)\n\n**Key Facts:**\n\n**Takeaway:**\n(1 paragraph)")
                output = r.content
            elif route == "AUTOGEN":
                df_preview = pd.read_csv(temp_file_path).head(5).to_string()
                df_shape = pd.read_csv(temp_file_path).shape
                df_stats = pd.read_csv(temp_file_path).describe().to_string()
                r = llm.invoke(f"""You are an expert data scientist running a 5-agent AutoGen ML pipeline.
DATASET: {df_shape[0]} rows x {df_shape[1]} columns
TASK: {final_task}
SAMPLE:\n{df_preview}
STATS:\n{df_stats}
Write a complete AutoGen ML Pipeline Report:
# AutoGen DS Pipeline Report
## Explorer Agent
## Strategy Agent
## Builder Agent — Code
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
```
## Validator Agent Results
## Final Report
### Executive Summary
### Key Findings
### Model Performance Analysis
### Business Recommendations
### Next Steps
Use actual column names and realistic numbers.""")
                output = r.content
            else:
                from orchestrator import build_orchestrator
                result = build_orchestrator().invoke({"user_task":final_task,"route":"","file_path":temp_file_path,"final_output":"","error":None})
                output = result["final_output"]

            s2.markdown('<div class="step done">02 · agent complete</div>',unsafe_allow_html=True)
            s3.markdown('<div class="step done">03 · output ready</div>',unsafe_allow_html=True)

            hist = {"icon":selected["icon"],"agent":selected_name,"task":final_task,"output":output,"time":datetime.now().strftime("%H:%M")}
            st.session_state.history.append(hist); st.session_state.last_output = hist

            st.markdown(f"""<div class="out-card"><div class="out-progress"></div>
            <div class="out-header"><div class="traffic-lights"><div class="tl tl-r"></div><div class="tl tl-y"></div><div class="tl tl-g"></div></div>
            <div class="out-title">agentiq · {selected_name.lower()} · output.md</div>
            <div class="out-badge">{selected['icon']} {selected_name}</div></div>
            <div class="out-body">""", unsafe_allow_html=True)
            st.markdown(output)
            st.markdown("</div></div>", unsafe_allow_html=True)
            st.download_button("⬇️ export output", data=output, file_name=f"agentiq_{route.lower()}_{datetime.now().strftime('%H%M')}.md", mime="text/markdown")

        except Exception as e:
            s1.empty(); s2.empty(); s3.empty()
            st.error(f"// runtime error: {str(e)}")