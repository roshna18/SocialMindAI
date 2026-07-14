import json
import streamlit as st
import streamlit.components.v1 as components
import subprocess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io, base64, hashlib
from datetime import datetime, timedelta

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="SocialMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global styles ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stAppViewContainer"] { background: #06091A; }
.block-container { max-width: 1200px; padding: 0 2rem 5rem; }
* { font-family: 'Inter', sans-serif !important; }

div[data-testid="stTextInput"] input {
    background: #0D1326 !important; border: 1px solid #1E2B45 !important;
    border-radius: 14px !important; color: #E8EEFF !important;
    font-size: 15px !important; padding: 15px 20px !important; height: auto !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #5B52C8 !important;
    box-shadow: 0 0 0 3px rgba(91,82,200,.18) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #2E3D58 !important; }
div[data-testid="stTextInput"] label { display:none !important; }

div[data-testid="stButton"] > button {
    background: #5B52C8 !important; color: #fff !important;
    border: none !important; border-radius: 12px !important;
    font-size: 14px !important; font-weight: 600 !important;
    padding: 12px 28px !important; height: auto !important; width: 100% !important;
    letter-spacing: .02em;
}
div[data-testid="stButton"] > button:hover { background: #7068D8 !important; }

[data-testid="stMetric"] {
    background: #0C1120 !important; border: 1px solid #182030 !important;
    border-radius: 16px !important; padding: 18px 22px !important;
}
[data-testid="stMetricLabel"] { color: #3A4F6E !important; font-size: 11px !important; letter-spacing: .08em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #E8EEFF !important; font-size: 26px !important; font-family: 'DM Mono', monospace !important; }

[data-testid="stExpander"] {
    background: #0C1120 !important; border: 1px solid #182030 !important;
    border-radius: 14px !important;
}
[data-testid="stExpander"] summary { color: #94A3B8 !important; font-size: 14px !important; font-weight: 500 !important; }

[data-testid="stTabs"] button { color: #3A4F6E !important; font-size: 13px !important; font-weight: 500 !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color: #E8EEFF !important; border-bottom-color: #5B52C8 !important; }

hr { border:none; border-top:1px solid #131E34 !important; margin:2rem 0 !important; }

.dl-link a {
    display:inline-flex; align-items:center; gap:8px;
    background:#0C1120; border:1px solid #182030; border-radius:10px;
    color:#9B8FEE !important; padding:10px 20px; font-size:13px;
    font-weight:500; text-decoration:none; letter-spacing:.02em;
}
.dl-link a:hover { background:#131E34; }
.mention-pill {
    font-size:13px; color:#94A3B8; padding:9px 14px; margin-bottom:8px;
    border-radius:0 8px 8px 0; display:block; line-height:1.55;
}
</style>
""", unsafe_allow_html=True)

# ── Chart constants ───────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#64748B", size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    xaxis=dict(gridcolor="#131E34", linecolor="#131E34", tickfont=dict(color="#64748B")),
    yaxis=dict(gridcolor="#131E34", linecolor="#131E34", tickfont=dict(color="#64748B")),
)
_LEGEND = dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B"))
PALETTE = ["#5B52C8","#1DAD85","#F0A030","#E2504A","#9B8FEE","#4EC9A0","#60A5FA"]


def _head():
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
        '&family=DM+Mono:wght@500&display=swap" rel="stylesheet">'
        '<style>*{font-family:Inter,sans-serif!important;box-sizing:border-box;margin:0;padding:0;}'
        'body{background:transparent;overflow:hidden;}</style>'
    )


# ── Chart helpers ─────────────────────────────────────────────
def styled_bar(df, x, y, orientation="v", title=""):
    fig = px.bar(df, x=x, y=y, orientation=orientation,
                 text=x if orientation=="h" else y,
                 color_discrete_sequence=PALETTE, title=title)
    fig.update_traces(marker_line_width=0, textposition="outside",
                      textfont=dict(color="#64748B", size=11))
    fig.update_layout(**CHART_LAYOUT, legend=_LEGEND, height=400)
    return fig

def styled_line(df, x, y, color="#5B52C8", title=""):
    fig = px.line(df, x=x, y=y, markers=True, title=title,
                  color_discrete_sequence=[color])
    fig.update_traces(line=dict(width=2), marker=dict(size=6))
    fig.update_layout(**CHART_LAYOUT, legend=_LEGEND, height=300)
    return fig

def donut_chart(pos, neu, neg):
    fig = px.pie(
        pd.DataFrame({"s":["Positive","Neutral","Negative"],"c":[pos,neu,neg]}),
        names="s", values="c", hole=0.74,
        color="s", color_discrete_map={"Positive":"#1DAD85","Neutral":"#475569","Negative":"#E2504A"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#CBD5E1"),
        height=400, margin=dict(l=10,r=10,t=30,b=10),
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


def lbl(text):
    st.markdown(
        f'<div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;'
        f'text-transform:uppercase;margin-bottom:12px;margin-top:6px;">{text}</div>',
        unsafe_allow_html=True,
    )


# ── HTML component builders ───────────────────────────────────
def score_ring_html(score, company, grade, g_bg, g_col, risk, r_bg, r_col, topic):
    pct  = max(0, min(score/100, 1))
    circ = 2*3.14159*34
    dash, gap = pct*circ, (1-pct)*circ
    ring_col = "#1DAD85" if score>=70 else "#F0A030" if score>=45 else "#E2504A"
    return f"""{_head()}
<div style="display:flex;align-items:center;gap:28px;
     background:#0C1120;border:1px solid #182030;border-radius:20px;padding:26px 30px;">
  <svg width="84" height="84" viewBox="0 0 84 84" style="flex-shrink:0">
    <circle cx="42" cy="42" r="34" fill="none" stroke="#182030" stroke-width="7"/>
    <circle cx="42" cy="42" r="34" fill="none" stroke="{ring_col}" stroke-width="7"
      stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-linecap="round"
      transform="rotate(-90 42 42)"/>
    <text x="42" y="48" text-anchor="middle" font-size="17" font-weight="700"
      fill="#E8EEFF" font-family="DM Mono,monospace">{score}</text>
  </svg>
  <div>
    <div style="font-size:23px;font-weight:700;color:#E8EEFF;letter-spacing:-0.03em;margin-bottom:5px;">{company}</div>
    <div style="font-size:11px;color:#2E3D58;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px;">Reputation intelligence</div>
    <span style="display:inline-block;font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;margin-right:6px;background:{g_bg};color:{g_col};">{grade} grade</span>
    <span style="display:inline-block;font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;margin-right:6px;background:{r_bg};color:{r_col};">{risk} risk</span>
    <span style="display:inline-block;font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;background:rgba(29,173,133,0.14);color:#4EC9A0;">{topic}</span>
  </div>
</div>"""

def stakeholder_html(s_scores):
    defaults = {"Customers":"#1DAD85","Investors":"#5B52C8","Media":"#F0A030","Employees":"#E2504A"}
    icons    = {"Customers":"👥","Investors":"📈","Media":"📰","Employees":"🏢"}
    def pick(v, d): return d if v>=60 else "#F0A030" if v>=35 else "#E2504A"
    rows = ""
    for lbl_name, val in s_scores.items():
        v = max(0, int(val))
        c = pick(v, defaults.get(lbl_name,"#5B52C8"))
        rows += f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
          <div style="width:20px;font-size:14px;">{icons.get(lbl_name,"•")}</div>
          <div style="font-size:13px;color:#64748B;width:76px;flex-shrink:0;">{lbl_name}</div>
          <div style="flex:1;height:5px;background:#182030;border-radius:3px;overflow:hidden;">
            <div style="height:100%;width:{v}%;background:{c};border-radius:3px;"></div>
          </div>
          <div style="font-size:13px;font-weight:600;color:#E8EEFF;width:30px;
               text-align:right;font-family:DM Mono,monospace;">{v}</div>
        </div>"""
    return f"""{_head()}
<div style="background:#0C1120;border:1px solid #182030;border-radius:16px;padding:22px 24px;">
  <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;text-transform:uppercase;margin-bottom:18px;">Stakeholder sentiment</div>
  {rows}
</div>"""

def crisis_radar_html(velocity, risk, alerts):
    vel_color = "#E2504A" if velocity=="High" else "#F0A030" if velocity=="Medium" else "#1DAD85"
    pulse = "animation:pulse 1.5s infinite;" if risk.upper()=="HIGH" else ""
    items = ""
    for a in alerts:
        lvl = a.get("level","info")
        bg  = {"critical":"rgba(226,80,74,.09)","warning":"rgba(240,160,48,.09)","info":"rgba(29,173,133,.09)"}.get(lvl,"rgba(29,173,133,.09)")
        bc  = {"critical":"rgba(226,80,74,.25)","warning":"rgba(240,160,48,.25)","info":"rgba(29,173,133,.25)"}.get(lvl,"rgba(29,173,133,.25)")
        dot = {"critical":"#E2504A","warning":"#F0A030","info":"#1DAD85"}.get(lvl,"#1DAD85")
        items += f"""<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;
               border-radius:10px;margin-bottom:8px;font-size:12.5px;line-height:1.55;
               background:{bg};border:1px solid {bc};color:#94A3B8;">
          <div style="width:7px;height:7px;border-radius:50%;background:{dot};margin-top:5px;flex-shrink:0;{pulse}"></div>
          <div>{a['text']}</div></div>"""
    return f"""{_head()}
<style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}</style>
<div style="background:#0C1120;border:1px solid #182030;border-radius:16px;padding:22px 24px;">
  <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;text-transform:uppercase;margin-bottom:14px;">⚡ Crisis radar</div>
  <div style="display:flex;gap:10px;margin-bottom:16px;">
    <div style="flex:1;background:#0F1830;border:1px solid #182030;border-radius:12px;padding:12px 16px;text-align:center;">
      <div style="font-size:10px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;">Velocity</div>
      <div style="font-size:17px;font-weight:700;color:{vel_color};font-family:DM Mono,monospace;">{velocity}</div>
    </div>
    <div style="flex:1;background:#0F1830;border:1px solid #182030;border-radius:12px;padding:12px 16px;text-align:center;">
      <div style="font-size:10px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;">Classification</div>
      <div style="font-size:17px;font-weight:700;color:{vel_color};font-family:DM Mono,monospace;">{risk}</div>
    </div>
  </div>
  {items}
</div>"""

def memo_html(score, grade, risk, top_issue, company):
    now = datetime.now().strftime("%B %d, %Y")
    risk_color = "#E2504A" if risk.upper()=="HIGH" else "#F0A030" if risk.upper()=="MEDIUM" else "#1DAD85"
    actions = [
        f"Increase executive transparency on <strong style='color:#E8EEFF;'>{top_issue.lower()}</strong>",
        "Accelerate internal communications to address employee sentiment",
        "Monitor media velocity daily until risk level normalises",
        "Brief investor relations team on current risk classification",
    ]
    action_items = "".join(
        f"<div style='display:flex;gap:10px;margin-bottom:8px;'>"
        f"<span style='color:#3A4F6E;font-size:12px;margin-top:2px;flex-shrink:0;'>0{i+1}</span>"
        f"<span>{a}</span></div>"
        for i, a in enumerate(actions)
    )
    return f"""{_head()}
<div style="background:#0C1120;border:1px solid #182030;border-left:3px solid #5B52C8;
     border-radius:16px;padding:26px 28px;font-size:13.5px;color:#64748B;line-height:1.85;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px;">
    <div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.18em;color:#5B52C8;text-transform:uppercase;margin-bottom:6px;">🧠 CEO Briefing Memo</div>
      <div style="font-size:20px;font-weight:700;color:#E8EEFF;letter-spacing:-0.02em;">{company} — Reputation Update</div>
    </div>
    <div style="font-size:12px;color:#2E3D58;">{now}</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:20px;">
    <div style="background:#0F1830;border:1px solid #182030;border-radius:10px;padding:14px 16px;">
      <div style="font-size:10px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;">Score</div>
      <div style="font-size:22px;font-weight:700;color:#E8EEFF;font-family:DM Mono,monospace;">{score}</div>
    </div>
    <div style="background:#0F1830;border:1px solid #182030;border-radius:10px;padding:14px 16px;">
      <div style="font-size:10px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;">Grade</div>
      <div style="font-size:22px;font-weight:700;color:#E8EEFF;font-family:DM Mono,monospace;">{grade}</div>
    </div>
    <div style="background:#0F1830;border:1px solid #182030;border-radius:10px;padding:14px 16px;">
      <div style="font-size:10px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;">Risk</div>
      <div style="font-size:22px;font-weight:700;color:{risk_color};font-family:DM Mono,monospace;">{risk}</div>
    </div>
  </div>
  <div style="margin-bottom:18px;">
    <strong style="color:#E8EEFF;">Executive summary</strong><br>
    Negative discussion is concentrated around <strong style="color:#E8EEFF;">{top_issue}</strong>.
    Public perception indicates a <strong style="color:#E8EEFF;">{risk.lower()} risk</strong> environment.
    Stakeholder trust is strongest with customers and requires immediate attention at the employee level.
  </div>
  <div><strong style="color:#E8EEFF;">Recommended actions</strong>
    <div style="margin-top:10px;">{action_items}</div>
  </div>
</div>"""


# ── COMPETITORS — full redesign ───────────────────────────────
# Each competitor entry now includes dimension scores + strength reasons
# Grade bands: 80+ Excellent, 65-79 Good, 50-64 Fair, <50 Weak
COMPETITOR_DB = {

    # ────────────────────────────── AI LABS ──────────────────────────────
    "openai": {
        "peers": [
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["ChatGPT — world's most recognised AI product", "GPT-4 benchmark leader", "Enterprise API dominance"],
             "weaknesses": ["Leadership instability (Altman saga)", "Safety criticism from researchers", "Profit vs mission tension"]},
            {"name": "Anthropic", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 82, "Leadership": 85, "ESG": 80, "Customer": 68},
             "strengths": ["Claude scores highest on safety benchmarks", "Strong Constitutional AI research", "Trusted by regulated industries"],
             "weaknesses": ["Lower brand recognition vs ChatGPT", "Smaller developer ecosystem", "Less media presence"]},
            {"name": "Google DeepMind", "score": 65, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 80, "Innovation": 85, "Leadership": 70, "ESG": 65, "Customer": 55},
             "strengths": ["Gemini integrated across Google products", "Massive research budget", "AlphaFold credibility"],
             "weaknesses": ["Gemini launch perception issues", "Privacy concerns tied to Google", "Slow enterprise adoption"]},
            {"name": "Mistral", "score": 60, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 45, "Innovation": 75, "Leadership": 72, "ESG": 60, "Customer": 50},
             "strengths": ["Open-source model reputation", "European AI champion narrative", "Lean & efficient models"],
             "weaknesses": ["Much smaller scale than US rivals", "Limited enterprise support", "Brand still building"]},
        ]
    },
    "anthropic": {
        "peers": [
            {"name": "Anthropic", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 82, "Leadership": 85, "ESG": 80, "Customer": 68},
             "strengths": ["Claude rated most trustworthy AI assistant", "Constitutional AI safety leadership", "Preferred in healthcare & legal sectors"],
             "weaknesses": ["ChatGPT has 10x more brand recognition", "Smaller plugin/integration ecosystem", "Lower consumer awareness"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["ChatGPT brand is synonymous with AI", "Largest developer community", "Most 3rd-party integrations"],
             "weaknesses": ["Safety controversy hurts trust score", "CEO drama hurt leadership perception", "Microsoft dependency"]},
            {"name": "Google DeepMind", "score": 65, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 80, "Innovation": 85, "Leadership": 70, "ESG": 65, "Customer": 55},
             "strengths": ["Distribution via Google Search & Workspace", "Best multimodal research", "Unlimited compute budget"],
             "weaknesses": ["Privacy baggage from Google brand", "Slower product iteration", "Gemini launch credibility gap"]},
        ]
    },
    "perplexity": {
        "peers": [
            {"name": "Perplexity", "score": 61, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 58, "Innovation": 75, "Leadership": 68, "ESG": 60, "Customer": 70},
             "strengths": ["Answer-engine UX praised by power users", "Fast citation-based search differentiation", "Strong app-store ratings"],
             "weaknesses": ["Tiny scale vs OpenAI/Google", "Dependent on third-party foundation models", "Monetization model still unproven"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["ChatGPT search feature reaches huge user base", "Deep model R&D advantage", "Enterprise distribution via API"],
             "weaknesses": ["Search still secondary to chat product", "Leadership instability", "Safety criticism"]},
            {"name": "Google", "score": 78, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 88, "Leadership": 78, "ESG": 72, "Customer": 68},
             "strengths": ["Search + AI Overviews reach billions", "Unmatched index & infrastructure", "Gemini integration across products"],
             "weaknesses": ["Slower to innovate on answer-engine UX", "Antitrust scrutiny", "Legacy ad-model tension with AI answers"]},
            {"name": "Anthropic", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 82, "Leadership": 85, "ESG": 80, "Customer": 68},
             "strengths": ["Model quality trusted for research tasks", "Strong safety reputation", "Growing enterprise trust"],
             "weaknesses": ["No dedicated consumer search product", "Smaller brand than Google/OpenAI", "Limited real-time web integration"]},
        ]
    },
    "google_deepmind": {
        "peers": [
            {"name": "Google DeepMind", "score": 65, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 80, "Innovation": 85, "Leadership": 70, "ESG": 65, "Customer": 55},
             "strengths": ["AlphaFold and scientific research credibility", "Distribution via Google's entire product suite", "Massive TPU compute budget"],
             "weaknesses": ["Gemini launch perception issues", "Slower enterprise-facing product iteration", "Privacy baggage from Google brand"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["ChatGPT brand dominance", "First-mover consumer AI habit", "Largest developer ecosystem"],
             "weaknesses": ["Leadership instability", "Safety criticism", "Heavy Microsoft dependency"]},
            {"name": "Anthropic", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 82, "Leadership": 85, "ESG": 80, "Customer": 68},
             "strengths": ["Safety-first research reputation", "Strong enterprise trust in regulated sectors", "Consistent leadership stability"],
             "weaknesses": ["Smaller brand recognition", "Less consumer product surface area", "Smaller compute footprint than Google"]},
        ]
    },
    "meta_ai": {
        "peers": [
            {"name": "Meta AI", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 65, "Innovation": 78, "Leadership": 50, "ESG": 45, "Customer": 55},
             "strengths": ["Llama open-source developer adoption", "Distribution via Instagram/WhatsApp/Facebook", "Free access drives usage volume"],
             "weaknesses": ["No standalone consumer brand identity", "Safety/misinformation criticism", "Monetization path still unclear"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["Standalone product with dedicated brand loyalty", "Strongest closed-model benchmarks", "Enterprise API revenue engine"],
             "weaknesses": ["Leadership instability", "Safety criticism", "Compute cost pressure"]},
            {"name": "Google DeepMind", "score": 65, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 80, "Innovation": 85, "Leadership": 70, "ESG": 65, "Customer": 55},
             "strengths": ["Broad multimodal research base", "Deep product integration across Google", "Long research track record"],
             "weaknesses": ["Gemini launch credibility gap", "Slower iteration cadence", "Privacy scrutiny"]},
            {"name": "Anthropic", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 82, "Leadership": 85, "ESG": 80, "Customer": 68},
             "strengths": ["Strong safety reputation", "Enterprise trust in regulated industries", "Stable leadership"],
             "weaknesses": ["No open-weight strategy to match Llama's reach", "Smaller consumer footprint", "Limited ad-supported distribution"]},
        ]
    },
    "xai": {
        "peers": [
            {"name": "xAI", "score": 55, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 60, "Innovation": 72, "Leadership": 45, "ESG": 35, "Customer": 48},
             "strengths": ["Grok integrated directly into X (Twitter)", "Elon Musk drives outsized media attention", "Access to X real-time data feed"],
             "weaknesses": ["Leadership controversy around content moderation", "Smaller research team than rivals", "ESG concerns over content policies"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["Far larger user base and brand trust", "Deeper enterprise partnerships", "More mature safety processes"],
             "weaknesses": ["Leadership instability", "Safety criticism", "Profit vs mission tension"]},
            {"name": "Anthropic", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 82, "Leadership": 85, "ESG": 80, "Customer": 68},
             "strengths": ["Strongest safety and trust reputation", "Stable, low-controversy leadership", "Preferred by regulated enterprises"],
             "weaknesses": ["Smaller brand recognition", "No social-platform distribution channel", "Slower consumer growth"]},
            {"name": "Google DeepMind", "score": 65, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 80, "Innovation": 85, "Leadership": 70, "ESG": 65, "Customer": 55},
             "strengths": ["Massive compute and research scale", "Broad product distribution", "Long-established research credibility"],
             "weaknesses": ["Gemini launch perception issues", "Slower iteration than nimble rivals", "Privacy scrutiny"]},
        ]
    },
    "mistral": {
        "peers": [
            {"name": "Mistral AI", "score": 60, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 45, "Innovation": 75, "Leadership": 72, "ESG": 60, "Customer": 50},
             "strengths": ["Open-source model reputation", "European AI champion narrative", "Lean & efficient models"],
             "weaknesses": ["Much smaller scale than US rivals", "Limited enterprise support", "Brand still building"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["Global brand dominance", "Largest developer ecosystem", "Frontier benchmark leadership"],
             "weaknesses": ["Leadership instability", "Safety criticism", "Heavy compute costs"]},
            {"name": "Meta AI", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 65, "Innovation": 78, "Leadership": 50, "ESG": 45, "Customer": 55},
             "strengths": ["Llama open-weight ecosystem scale", "Massive built-in distribution", "Free-to-use developer goodwill"],
             "weaknesses": ["No standalone brand identity", "Misinformation/safety criticism", "Unclear monetization"]},
            {"name": "Anthropic", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 82, "Leadership": 85, "ESG": 80, "Customer": 68},
             "strengths": ["Strongest safety reputation", "Deep enterprise trust", "Stable leadership"],
             "weaknesses": ["Closed-weight strategy limits developer reach", "Smaller brand than OpenAI", "Higher price point for SMBs"]},
        ]
    },
    "cohere": {
        "peers": [
            {"name": "Cohere", "score": 56, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 38, "Innovation": 68, "Leadership": 65, "ESG": 58, "Customer": 60},
             "strengths": ["Enterprise-focused RAG/retrieval strength", "Strong North American enterprise partnerships", "Data-privacy positioning for regulated clients"],
             "weaknesses": ["Low consumer brand awareness", "Smaller model scale than frontier labs", "Limited marketing budget"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["Vastly larger brand and developer base", "Broader model capability range", "Faster product iteration"],
             "weaknesses": ["Leadership instability", "Safety criticism", "Less specialised for enterprise search"]},
            {"name": "Anthropic", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 82, "Leadership": 85, "ESG": 80, "Customer": 68},
             "strengths": ["Strong enterprise trust and safety record", "Stable leadership", "Growing regulated-industry adoption"],
             "weaknesses": ["Smaller brand than OpenAI", "Fewer enterprise search-specific tools", "Premium pricing"]},
            {"name": "Mistral AI", "score": 60, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 45, "Innovation": 75, "Leadership": 72, "ESG": 60, "Customer": 50},
             "strengths": ["Open-source model credibility", "European data-sovereignty appeal", "Efficient, lower-cost models"],
             "weaknesses": ["Small enterprise sales team", "Limited North American presence", "Brand still building"]},
        ]
    },
    "character_ai": {
        "peers": [
            {"name": "Character.AI", "score": 48, "grade": "Weak", "risk": "High",
             "dims": {"Brand": 50, "Innovation": 62, "Leadership": 42, "ESG": 35, "Customer": 65},
             "strengths": ["High engagement among Gen Z users", "Novel companion-chat product category", "Strong daily session times"],
             "weaknesses": ["Child-safety and wellbeing scrutiny", "Thin monetization model", "Acquihire uncertainty after Google deal"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["Far larger and more diversified user base", "Stronger safety infrastructure", "Broader brand trust"],
             "weaknesses": ["Leadership instability", "Less focused on companion-chat niche", "Safety criticism of its own"]},
            {"name": "Meta AI", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 65, "Innovation": 78, "Leadership": 50, "ESG": 45, "Customer": 55},
             "strengths": ["Built-in distribution across Instagram/WhatsApp", "AI persona features rolling out at scale", "Large existing user relationships"],
             "weaknesses": ["Teen-safety controversy of its own", "No standalone AI brand", "Monetization path unclear"]},
            {"name": "xAI", "score": 55, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 60, "Innovation": 72, "Leadership": 45, "ESG": 35, "Customer": 48},
             "strengths": ["Companion-style Grok personas gaining attention", "High media visibility", "Direct X platform distribution"],
             "weaknesses": ["Leadership/content controversy", "Smaller research team", "ESG concerns"]},
        ]
    },
    "huggingface": {
        "peers": [
            {"name": "Hugging Face", "score": 63, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 55, "Innovation": 78, "Leadership": 70, "ESG": 70, "Customer": 72},
             "strengths": ["De facto hub for open-source model hosting", "Trusted neutral platform across the developer community", "Strong ties with every major AI lab"],
             "weaknesses": ["Limited proprietary frontier models", "Revenue model less proven than cloud rivals", "Smaller compute resources than Big Tech"]},
            {"name": "OpenAI", "score": 68, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 90, "Innovation": 88, "Leadership": 55, "ESG": 50, "Customer": 65},
             "strengths": ["Frontier closed-model performance lead", "Massive brand recognition", "Enterprise API revenue scale"],
             "weaknesses": ["Leadership instability", "Less open/community-oriented model", "Safety criticism"]},
            {"name": "Meta AI", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 65, "Innovation": 78, "Leadership": 50, "ESG": 45, "Customer": 55},
             "strengths": ["Llama models widely hosted and used", "Deep pockets to subsidize open weights", "Massive distribution reach"],
             "weaknesses": ["No dedicated hosting/tooling platform brand", "Safety/misinformation criticism", "Unclear monetization"]},
            {"name": "Mistral AI", "score": 60, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 45, "Innovation": 75, "Leadership": 72, "ESG": 60, "Customer": 50},
             "strengths": ["Open-weight model releases align with HF's mission", "European AI champion narrative", "Efficient, lean models"],
             "weaknesses": ["Much smaller scale than US labs", "Limited enterprise support", "Brand still building"]},
        ]
    },

    # ─────────────────────────── CONSUMER ELECTRONICS ───────────────────────────
    "apple": {
        "peers": [
            {"name": "Apple", "score": 85, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 98, "Innovation": 82, "Leadership": 88, "ESG": 80, "Customer": 90},
             "strengths": ["Strongest consumer brand on earth", "iPhone ecosystem lock-in", "Premium pricing power"],
             "weaknesses": ["AI features perceived as behind Google/OpenAI", "China manufacturing dependency", "App Store antitrust pressure"]},
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Galaxy AI features ahead in Android space", "Semiconductor vertical integration", "#1 display technology"],
             "weaknesses": ["Software experience trails Apple", "Brand less premium in West", "Foldable reliability concerns"]},
            {"name": "Google", "score": 78, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 88, "Leadership": 78, "ESG": 72, "Customer": 68},
             "strengths": ["Android controls majority of global smartphones", "Tensor chip AI integration", "Google Assistant + Gemini"],
             "weaknesses": ["Pixel hardware brand still niche", "Privacy perception issues", "Hardware profitability low"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Satya Nadella seen as best Big Tech CEO", "Copilot AI integration across Office", "Azure cloud dominance"],
             "weaknesses": ["Consumer brand less exciting than Apple", "Teams still trails Slack in NPS", "Gaming strategy mixed"]},
        ]
    },
    "samsung": {
        "peers": [
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Broadest product range from chips to foldables", "Vertical integration (memory, displays, foundry)", "Galaxy AI ahead in Android space"],
             "weaknesses": ["Brand seen as less premium than Apple in the West", "Software experience trails Apple", "Foldable reliability concerns"]},
            {"name": "Apple", "score": 85, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 98, "Innovation": 82, "Leadership": 88, "ESG": 80, "Customer": 90},
             "strengths": ["Strongest consumer brand loyalty on earth", "Tight hardware-software integration", "Premium pricing power"],
             "weaknesses": ["AI features perceived as behind Google/Samsung", "China manufacturing dependency", "App Store antitrust pressure"]},
            {"name": "Xiaomi", "score": 62, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 65, "ESG": 58, "Customer": 68},
             "strengths": ["Best value-for-money positioning globally", "Fast-growing EV + IoT ecosystem", "#3 global smartphone shipments"],
             "weaknesses": ["Thinner margins than premium rivals", "Brand seen as budget outside home market", "Regulatory scrutiny in some markets"]},
            {"name": "Huawei", "score": 57, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 65, "Innovation": 80, "Leadership": 55, "ESG": 45, "Customer": 55},
             "strengths": ["Vertical chip design resilience under sanctions", "Strong domestic China loyalty", "5G/telecom infrastructure leadership"],
             "weaknesses": ["US export ban restricts global growth", "Limited Google services access", "Geopolitical trust concerns in West"]},
        ]
    },
    "sony": {
        "peers": [
            {"name": "Sony", "score": 68, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 74, "Leadership": 70, "ESG": 68, "Customer": 70},
             "strengths": ["PlayStation ecosystem loyalty", "Best-in-class camera sensor technology", "Strong brand trust in imaging/audio"],
             "weaknesses": ["Mobile division niche outside Japan", "Slower AI feature rollout", "Complex conglomerate structure"]},
            {"name": "Apple", "score": 85, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 98, "Innovation": 82, "Leadership": 88, "ESG": 80, "Customer": 90},
             "strengths": ["Ecosystem lock-in across hardware categories", "Premium brand and pricing power", "Deep AI/software investment"],
             "weaknesses": ["No dedicated gaming console business", "China manufacturing dependency", "App Store antitrust pressure"]},
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Display and sensor vertical integration rivals Sony", "Broader consumer electronics portfolio", "Galaxy AI momentum"],
             "weaknesses": ["Camera brand prestige trails Sony in imaging", "Software experience seen as weaker", "Foldable reliability concerns"]},
            {"name": "Xiaomi", "score": 62, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 65, "ESG": 58, "Customer": 68},
             "strengths": ["Aggressive value pricing across categories", "Fast-growing ecosystem of connected devices", "Rapid global expansion"],
             "weaknesses": ["Lower brand prestige than Sony in imaging/audio", "Thinner margins", "Regulatory scrutiny in some markets"]},
        ]
    },
    "xiaomi": {
        "peers": [
            {"name": "Xiaomi", "score": 62, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 65, "ESG": 58, "Customer": 68},
             "strengths": ["Best value-for-money positioning globally", "Fast-growing EV + IoT ecosystem", "#3 global smartphone shipments"],
             "weaknesses": ["Thinner margins than premium rivals", "Brand seen as budget outside home market", "Regulatory scrutiny in some markets"]},
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Stronger premium brand perception", "Deep vertical integration", "Broader global retail presence"],
             "weaknesses": ["Higher price points limit value-segment reach", "Software experience trails Apple", "Foldable reliability concerns"]},
            {"name": "Apple", "score": 85, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 98, "Innovation": 82, "Leadership": 88, "ESG": 80, "Customer": 90},
             "strengths": ["Unmatched premium brand loyalty", "Ecosystem lock-in", "Highest margins in the industry"],
             "weaknesses": ["No budget-tier products to compete with Xiaomi", "China manufacturing dependency", "App Store antitrust pressure"]},
            {"name": "Huawei", "score": 57, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 65, "Innovation": 80, "Leadership": 55, "ESG": 45, "Customer": 55},
             "strengths": ["Strong domestic China loyalty", "Vertical chip design resilience", "5G/telecom infrastructure leadership"],
             "weaknesses": ["US export ban restricts global growth", "Limited Google services access", "Geopolitical trust concerns in West"]},
        ]
    },
    "huawei": {
        "peers": [
            {"name": "Huawei", "score": 57, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 65, "Innovation": 80, "Leadership": 55, "ESG": 45, "Customer": 55},
             "strengths": ["Vertical chip design resilience under sanctions", "Strong domestic China loyalty", "5G/telecom infrastructure leadership"],
             "weaknesses": ["US export ban restricts global growth", "Limited Google services access", "Geopolitical trust concerns in West"]},
            {"name": "Xiaomi", "score": 62, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 65, "ESG": 58, "Customer": 68},
             "strengths": ["Full global market access (no sanctions)", "Best value-for-money positioning", "Fast-growing IoT ecosystem"],
             "weaknesses": ["Thinner margins than premium rivals", "Brand seen as budget outside home market", "Regulatory scrutiny in some markets"]},
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Unrestricted global distribution", "Full Google services access", "Deep semiconductor vertical integration"],
             "weaknesses": ["Software experience trails Apple", "Brand less premium in West", "Foldable reliability concerns"]},
            {"name": "Apple", "score": 85, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 98, "Innovation": 82, "Leadership": 88, "ESG": 80, "Customer": 90},
             "strengths": ["Strongest global consumer brand", "Premium ecosystem lock-in", "No geopolitical export bans"],
             "weaknesses": ["China manufacturing dependency", "AI features perceived as behind rivals", "App Store antitrust pressure"]},
        ]
    },
    "oneplus": {
        "peers": [
            {"name": "OnePlus", "score": 55, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 50, "Innovation": 68, "Leadership": 58, "ESG": 55, "Customer": 65},
             "strengths": ["Enthusiast community brand loyalty", "Fast software update cadence", "Strong price-to-performance flagship specs"],
             "weaknesses": ["Small global market share", "Parent company (BBK) brand overlap confusion", "Limited carrier partnerships in US"]},
            {"name": "Xiaomi", "score": 62, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 65, "ESG": 58, "Customer": 68},
             "strengths": ["Broader product ecosystem beyond phones", "Larger global scale", "Faster international expansion"],
             "weaknesses": ["Thinner margins than premium rivals", "Brand seen as budget outside home market", "Regulatory scrutiny in some markets"]},
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Vastly larger global retail and carrier presence", "Deep vertical integration", "Broader premium/foldable lineup"],
             "weaknesses": ["Software experience trails Apple", "Brand less premium in West", "Foldable reliability concerns"]},
            {"name": "Apple", "score": 85, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 98, "Innovation": 82, "Leadership": 88, "ESG": 80, "Customer": 90},
             "strengths": ["Unmatched premium brand loyalty", "Ecosystem lock-in", "Highest margins and retail presence"],
             "weaknesses": ["AI features perceived as behind rivals", "China manufacturing dependency", "App Store antitrust pressure"]},
        ]
    },

    # ─────────────────────────────── SEMICONDUCTORS ───────────────────────────────
    "nvidia": {
        "peers": [
            {"name": "Nvidia", "score": 80, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 92, "Leadership": 88, "ESG": 65, "Customer": 78},
             "strengths": ["H100/H200 GPU monopoly for AI training", "CUDA ecosystem lock-in", "Jensen Huang seen as visionary CEO"],
             "weaknesses": ["Export control risks to China", "Single-product revenue concentration", "Supply constraints"]},
            {"name": "AMD", "score": 67, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 72, "Innovation": 78, "Leadership": 74, "ESG": 68, "Customer": 70},
             "strengths": ["ROCm open-source alternative to CUDA", "Strong CPU+GPU combined roadmap", "MI300X competitive on price"],
             "weaknesses": ["Software ecosystem trails Nvidia", "Lower AI mindshare", "Smaller data centre footprint"]},
            {"name": "Intel", "score": 54, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 70, "Innovation": 58, "Leadership": 55, "ESG": 65, "Customer": 55},
             "strengths": ["Gaudi3 AI accelerator gaining traction", "x86 installed base advantage", "US manufacturing credibility"],
             "weaknesses": ["Years behind in GPU performance", "Gaudi ecosystem very early", "Multiple execution stumbles"]},
        ]
    },
    "amd": {
        "peers": [
            {"name": "AMD", "score": 67, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 72, "Innovation": 78, "Leadership": 74, "ESG": 68, "Customer": 70},
             "strengths": ["ROCm open-source alternative to CUDA", "Strong CPU+GPU combined roadmap", "MI300X competitive on price"],
             "weaknesses": ["Software ecosystem trails Nvidia", "Lower AI mindshare", "Smaller data centre footprint"]},
            {"name": "Nvidia", "score": 80, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 92, "Leadership": 88, "ESG": 65, "Customer": 78},
             "strengths": ["Dominant CUDA software moat", "Category-defining AI training GPUs", "Visionary CEO leadership"],
             "weaknesses": ["Export control risks to China", "Single-product revenue concentration", "Supply constraints"]},
            {"name": "Intel", "score": 54, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 70, "Innovation": 58, "Leadership": 55, "ESG": 65, "Customer": 55},
             "strengths": ["x86 installed base advantage", "US manufacturing/CHIPS Act credibility", "Broad product portfolio"],
             "weaknesses": ["Years behind in GPU performance", "Gaudi ecosystem very early", "Multiple execution stumbles"]},
            {"name": "Qualcomm", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 80, "Leadership": 72, "ESG": 65, "Customer": 68},
             "strengths": ["Snapdragon dominant in premium Android", "Modem/connectivity IP licensing moat", "Growing automotive & PC chip push"],
             "weaknesses": ["Heavy dependence on smartphone cycles", "Limited data-centre GPU presence", "China market regulatory exposure"]},
        ]
    },
    "intel": {
        "peers": [
            {"name": "Intel", "score": 54, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 70, "Innovation": 58, "Leadership": 55, "ESG": 65, "Customer": 55},
             "strengths": ["Gaudi3 AI accelerator gaining traction", "x86 installed base advantage", "US manufacturing credibility"],
             "weaknesses": ["Years behind in GPU performance", "Gaudi ecosystem very early", "Multiple execution stumbles"]},
            {"name": "TSMC", "score": 84, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 92, "Leadership": 85, "ESG": 70, "Customer": 80},
             "strengths": ["Unmatched leading-edge foundry process yields", "Manufactures for nearly every major chip designer", "Deep customer trust and capacity commitments"],
             "weaknesses": ["Geopolitical risk concentrated in Taiwan", "Capital intensity limits flexibility", "US/Japan expansion execution risk"]},
            {"name": "Nvidia", "score": 80, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 92, "Leadership": 88, "ESG": 65, "Customer": 78},
             "strengths": ["Dominant AI GPU market share", "CUDA software moat", "Visionary CEO leadership"],
             "weaknesses": ["Export control risks to China", "Single-product revenue concentration", "Supply constraints"]},
            {"name": "AMD", "score": 67, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 72, "Innovation": 78, "Leadership": 74, "ESG": 68, "Customer": 70},
             "strengths": ["Competitive CPU roadmap gaining server share", "MI300X price-competitive AI accelerator", "Improving execution track record"],
             "weaknesses": ["Software ecosystem trails Nvidia", "Lower AI mindshare", "Smaller data centre footprint"]},
        ]
    },
    "qualcomm": {
        "peers": [
            {"name": "Qualcomm", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 80, "Leadership": 72, "ESG": 65, "Customer": 68},
             "strengths": ["Snapdragon dominant in premium Android", "Modem/connectivity IP licensing moat", "Growing automotive & PC chip push"],
             "weaknesses": ["Heavy dependence on smartphone cycles", "Apple modem business at risk", "China market regulatory exposure"]},
            {"name": "MediaTek", "score": 65, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 52, "Innovation": 74, "Leadership": 68, "ESG": 60, "Customer": 65},
             "strengths": ["Dominant in mid-range/budget smartphone chips", "Fast-growing share in flagship tier", "Diversified into smart TV & IoT chips"],
             "weaknesses": ["Lower brand prestige than Qualcomm", "Thinner margins on volume chips", "Heavy China market dependence"]},
            {"name": "Broadcom", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 80, "Leadership": 82, "ESG": 62, "Customer": 70},
             "strengths": ["Custom AI ASIC partnerships with hyperscalers", "Networking chip market leadership", "Strong free cash flow and M&A track record"],
             "weaknesses": ["Complex conglomerate perception", "VMware acquisition integration risk", "Customer concentration in a few hyperscalers"]},
            {"name": "Nvidia", "score": 80, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 92, "Leadership": 88, "ESG": 65, "Customer": 78},
             "strengths": ["Dominant AI training/inference GPU share", "CUDA ecosystem lock-in", "Visionary CEO leadership"],
             "weaknesses": ["Export control risks to China", "Single-product revenue concentration", "Supply constraints"]},
        ]
    },
    "broadcom": {
        "peers": [
            {"name": "Broadcom", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 80, "Leadership": 82, "ESG": 62, "Customer": 70},
             "strengths": ["Custom AI ASIC partnerships with hyperscalers", "Networking chip market leadership", "Strong free cash flow and M&A track record"],
             "weaknesses": ["Complex conglomerate perception", "VMware acquisition integration risk", "Customer concentration in a few hyperscalers"]},
            {"name": "Nvidia", "score": 80, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 92, "Leadership": 88, "ESG": 65, "Customer": 78},
             "strengths": ["Dominant merchant AI GPU market", "CUDA ecosystem lock-in", "Broadest AI developer mindshare"],
             "weaknesses": ["Export control risks to China", "Single-product revenue concentration", "Supply constraints"]},
            {"name": "Qualcomm", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 80, "Leadership": 72, "ESG": 65, "Customer": 68},
             "strengths": ["Snapdragon dominant in premium Android", "Strong IP licensing moat", "Growing automotive & PC chip push"],
             "weaknesses": ["Heavy dependence on smartphone cycles", "Smaller custom-silicon business than Broadcom", "China market regulatory exposure"]},
            {"name": "Marvell", "score": 66, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 48, "Innovation": 78, "Leadership": 70, "ESG": 60, "Customer": 62},
             "strengths": ["Custom AI silicon design wins with hyperscalers", "Strong networking/data infrastructure portfolio", "Growing optical interconnect business"],
             "weaknesses": ["Smaller scale than Broadcom/Nvidia", "Revenue concentration in few large customers", "Lower consumer brand recognition"]},
        ]
    },
    "arm": {
        "peers": [
            {"name": "ARM", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 62, "Innovation": 85, "Leadership": 75, "ESG": 68, "Customer": 65},
             "strengths": ["Architecture licensed in nearly all mobile chips", "Expanding into data centre & AI compute", "Neutral IP licensing model favored broadly"],
             "weaknesses": ["Revenue tied to royalty rates, not hardware margins", "SoftBank ownership overhang", "Nvidia acquisition attempt created uncertainty"]},
            {"name": "Qualcomm", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 80, "Leadership": 72, "ESG": 65, "Customer": 68},
             "strengths": ["Largest single licensee/customer of ARM architecture", "Strong modem/connectivity IP moat", "Growing PC/automotive chip push"],
             "weaknesses": ["Dependent on ARM's licensing terms", "Heavy dependence on smartphone cycles", "China market regulatory exposure"]},
            {"name": "Intel", "score": 54, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 70, "Innovation": 58, "Leadership": 55, "ESG": 65, "Customer": 55},
             "strengths": ["x86 architecture still dominant in PCs/servers", "US manufacturing credibility", "Broad product portfolio"],
             "weaknesses": ["Losing share to ARM-based designs (Apple Silicon)", "Years behind in GPU performance", "Multiple execution stumbles"]},
            {"name": "Nvidia", "score": 80, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 92, "Leadership": 88, "ESG": 65, "Customer": 78},
             "strengths": ["Increasingly builds ARM-based data-centre CPUs", "Dominant AI compute ecosystem", "Visionary CEO leadership"],
             "weaknesses": ["Failed acquisition of ARM drew regulatory scrutiny", "Export control risks to China", "Single-product revenue concentration"]},
        ]
    },
    "tsmc": {
        "peers": [
            {"name": "TSMC", "score": 84, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 92, "Leadership": 85, "ESG": 70, "Customer": 80},
             "strengths": ["Unmatched leading-edge foundry process yields", "Manufactures for nearly every major chip designer", "Deep customer trust and capacity commitments"],
             "weaknesses": ["Geopolitical risk concentrated in Taiwan", "Capital intensity limits flexibility", "US/Japan expansion execution risk"]},
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Only other foundry at leading-edge nodes", "Vertical integration with memory business", "Diversified beyond pure foundry"],
             "weaknesses": ["Trails TSMC in yield and customer trust", "Foundry business unit less profitable", "Geopolitical exposure lower but growing"]},
            {"name": "Intel", "score": 54, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 70, "Innovation": 58, "Leadership": 55, "ESG": 65, "Customer": 55},
             "strengths": ["US-based manufacturing pitched as geopolitical hedge", "CHIPS Act government support", "Foundry ambitions (Intel Foundry)"],
             "weaknesses": ["Years behind TSMC in process leadership", "Foundry customer trust still nascent", "Multiple execution stumbles"]},
            {"name": "Micron", "score": 63, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 75, "Leadership": 65, "ESG": 62, "Customer": 60},
             "strengths": ["Leading US-based memory manufacturer", "HBM demand surge from AI datacenters", "Government CHIPS Act support"],
             "weaknesses": ["Memory pricing highly cyclical", "Behind SK Hynix in HBM market share", "China export restrictions exposure"]},
        ]
    },
    "mediatek": {
        "peers": [
            {"name": "MediaTek", "score": 65, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 52, "Innovation": 74, "Leadership": 68, "ESG": 60, "Customer": 65},
             "strengths": ["Dominant in mid-range/budget smartphone chips", "Fast-growing share in flagship tier", "Diversified into smart TV & IoT chips"],
             "weaknesses": ["Lower brand prestige than Qualcomm", "Thinner margins on volume chips", "Heavy China market dependence"]},
            {"name": "Qualcomm", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 80, "Leadership": 72, "ESG": 65, "Customer": 68},
             "strengths": ["Stronger flagship/premium Snapdragon brand", "Deep modem/connectivity IP moat", "Growing automotive & PC chip push"],
             "weaknesses": ["Heavy dependence on smartphone cycles", "Apple modem business at risk", "China market regulatory exposure"]},
            {"name": "Broadcom", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 80, "Leadership": 82, "ESG": 62, "Customer": 70},
             "strengths": ["Custom AI ASIC partnerships with hyperscalers", "Diversified enterprise networking portfolio", "Strong free cash flow"],
             "weaknesses": ["Complex conglomerate perception", "Not focused on mobile SoCs", "Customer concentration risk"]},
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Exynos chips plus broader semiconductor scale", "Vertical integration advantage", "Strong global brand"],
             "weaknesses": ["Exynos trails Qualcomm/MediaTek in adoption", "Software experience trails Apple", "Foldable reliability concerns"]},
        ]
    },
    "micron": {
        "peers": [
            {"name": "Micron", "score": 63, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 75, "Leadership": 65, "ESG": 62, "Customer": 60},
             "strengths": ["Leading US-based memory manufacturer", "HBM demand surge from AI datacenters", "Government CHIPS Act support"],
             "weaknesses": ["Memory pricing highly cyclical", "Behind SK Hynix in HBM market share", "China export restrictions exposure"]},
            {"name": "Samsung", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 80, "Leadership": 70, "ESG": 68, "Customer": 72},
             "strengths": ["Largest global memory manufacturer by volume", "Deep vertical integration", "Broad diversification beyond memory"],
             "weaknesses": ["Memory pricing highly cyclical for all players", "Foundry business unit less profitable", "Software experience trails Apple"]},
            {"name": "TSMC", "score": 84, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 92, "Leadership": 85, "ESG": 70, "Customer": 80},
             "strengths": ["Unmatched logic foundry process leadership", "Manufactures for nearly every major chip designer", "Deep customer trust"],
             "weaknesses": ["Not a memory manufacturer directly", "Geopolitical risk concentrated in Taiwan", "Capital intensity limits flexibility"]},
            {"name": "Marvell", "score": 66, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 48, "Innovation": 78, "Leadership": 70, "ESG": 60, "Customer": 62},
             "strengths": ["Custom AI silicon design wins with hyperscalers", "Growing optical interconnect business", "Strong networking portfolio"],
             "weaknesses": ["Not a memory manufacturer", "Smaller scale than Micron", "Revenue concentration in few large customers"]},
        ]
    },
    "marvell": {
        "peers": [
            {"name": "Marvell", "score": 66, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 48, "Innovation": 78, "Leadership": 70, "ESG": 60, "Customer": 62},
             "strengths": ["Custom AI silicon design wins with hyperscalers", "Strong networking/data infrastructure portfolio", "Growing optical interconnect business"],
             "weaknesses": ["Smaller scale than Broadcom/Nvidia", "Revenue concentration in few large customers", "Lower consumer brand recognition"]},
            {"name": "Broadcom", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 80, "Leadership": 82, "ESG": 62, "Customer": 70},
             "strengths": ["Larger scale custom AI ASIC business", "Networking chip market leadership", "Strong free cash flow and M&A track record"],
             "weaknesses": ["Complex conglomerate perception", "VMware acquisition integration risk", "Customer concentration in a few hyperscalers"]},
            {"name": "Nvidia", "score": 80, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 92, "Leadership": 88, "ESG": 65, "Customer": 78},
             "strengths": ["Dominant merchant AI GPU market share", "CUDA ecosystem lock-in", "Broadest AI developer mindshare"],
             "weaknesses": ["Export control risks to China", "Single-product revenue concentration", "Supply constraints"]},
            {"name": "Qualcomm", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 80, "Leadership": 72, "ESG": 65, "Customer": 68},
             "strengths": ["Larger scale and stronger consumer brand", "Deep modem/connectivity IP moat", "Growing automotive & PC chip push"],
             "weaknesses": ["Heavy dependence on smartphone cycles", "Less focused on data-centre custom silicon", "China market regulatory exposure"]},
        ]
    },

    # ─────────────────────────────────── EVs ───────────────────────────────────
    "tesla": {
        "peers": [
            {"name": "Tesla", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 90, "Leadership": 48, "ESG": 60, "Customer": 65},
             "strengths": ["First-mover EV brand recognition", "Supercharger network moat", "FSD technology lead"],
             "weaknesses": ["CEO controversy drags leadership score", "Inconsistent build quality complaints"]},
            {"name": "Rivian", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 70, "Leadership": 65, "ESG": 75, "Customer": 50},
             "strengths": ["Strong ESG narrative", "Adventure/outdoor brand appeal", "Amazon partnership"],
             "weaknesses": ["Production ramp struggles", "Limited charging network", "Burning cash"]},
            {"name": "Lucid", "score": 49, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 45, "Innovation": 72, "Leadership": 52, "ESG": 60, "Customer": 42},
             "strengths": ["Best-in-class range specs", "Luxury positioning", "Saudi Aramco backing"],
             "weaknesses": ["Very low production volumes", "Low brand awareness", "Profitability concerns"]},
            {"name": "Ford EV", "score": 54, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 70, "Innovation": 55, "Leadership": 60, "ESG": 55, "Customer": 58},
             "strengths": ["F-150 Lightning brand trust", "Established dealer network", "Manufacturing scale"],
             "weaknesses": ["Late EV entrant", "Software experience behind Tesla", "EV division losses"]},
        ]
    },
    "byd": {
        "peers": [
            {"name": "BYD", "score": 75, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 68, "Innovation": 80, "Leadership": 75, "ESG": 70, "Customer": 72},
             "strengths": ["World's largest EV/PHEV seller by volume", "Vertically integrated battery production", "Aggressive international expansion"],
             "weaknesses": ["Brand perception still building outside China", "Tariff barriers in US/EU markets", "Margin pressure from price wars"]},
            {"name": "Tesla", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 90, "Leadership": 48, "ESG": 60, "Customer": 65},
             "strengths": ["Stronger global brand recognition", "Supercharger network moat", "FSD technology lead"],
             "weaknesses": ["CEO controversy drags leadership score", "Smaller PHEV/hybrid lineup", "Higher price points than BYD"]},
            {"name": "NIO", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 55, "Innovation": 72, "Leadership": 55, "ESG": 65, "Customer": 68},
             "strengths": ["Battery-swap infrastructure differentiation", "Premium brand positioning in China", "Strong owner community loyalty"],
             "weaknesses": ["Persistent cash burn and losses", "Limited presence outside China", "Execution risk on new sub-brands"]},
            {"name": "XPeng", "score": 54, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 48, "Innovation": 78, "Leadership": 58, "ESG": 62, "Customer": 60},
             "strengths": ["Advanced ADAS/autonomous driving tech", "Strong smart-cockpit software experience", "Volkswagen strategic partnership"],
             "weaknesses": ["Smaller sales volume than BYD/Tesla", "Continued profitability challenges", "Brand awareness low outside China"]},
        ]
    },
    "rivian": {
        "peers": [
            {"name": "Rivian", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 70, "Leadership": 65, "ESG": 75, "Customer": 50},
             "strengths": ["Strong ESG narrative", "Adventure/outdoor brand appeal", "Amazon partnership"],
             "weaknesses": ["Production ramp struggles", "Limited charging network", "Burning cash"]},
            {"name": "Tesla", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 90, "Leadership": 48, "ESG": 60, "Customer": 65},
             "strengths": ["First-mover EV brand recognition", "Supercharger network moat", "FSD technology lead"],
             "weaknesses": ["CEO controversy drags leadership score", "Inconsistent build quality complaints"]},
            {"name": "Lucid", "score": 49, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 45, "Innovation": 72, "Leadership": 52, "ESG": 60, "Customer": 42},
             "strengths": ["Best-in-class range specs", "Luxury positioning", "Saudi Aramco backing"],
             "weaknesses": ["Very low production volumes", "Low brand awareness", "Profitability concerns"]},
            {"name": "Ford EV", "score": 54, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 70, "Innovation": 55, "Leadership": 60, "ESG": 55, "Customer": 58},
             "strengths": ["F-150 Lightning brand trust", "Established dealer network", "Manufacturing scale"],
             "weaknesses": ["Late EV entrant", "Software experience behind Tesla", "EV division losses"]},
        ]
    },
    "lucid": {
        "peers": [
            {"name": "Lucid", "score": 49, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 45, "Innovation": 72, "Leadership": 52, "ESG": 60, "Customer": 42},
             "strengths": ["Best-in-class range specs", "Luxury positioning", "Saudi Aramco backing"],
             "weaknesses": ["Very low production volumes", "Low brand awareness", "Profitability concerns"]},
            {"name": "Tesla", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 90, "Leadership": 48, "ESG": 60, "Customer": 65},
             "strengths": ["First-mover EV brand recognition", "Supercharger network moat", "FSD technology lead"],
             "weaknesses": ["CEO controversy drags leadership score", "Inconsistent build quality complaints"]},
            {"name": "Rivian", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 70, "Leadership": 65, "ESG": 75, "Customer": 50},
             "strengths": ["Strong ESG narrative", "Adventure/outdoor brand appeal", "Amazon partnership"],
             "weaknesses": ["Production ramp struggles", "Limited charging network", "Burning cash"]},
            {"name": "NIO", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 55, "Innovation": 72, "Leadership": 55, "ESG": 65, "Customer": 68},
             "strengths": ["Battery-swap infrastructure differentiation", "Premium brand positioning in China", "Strong owner community loyalty"],
             "weaknesses": ["Persistent cash burn and losses", "Limited presence outside China", "Execution risk on new sub-brands"]},
        ]
    },
    "nio": {
        "peers": [
            {"name": "NIO", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 55, "Innovation": 72, "Leadership": 55, "ESG": 65, "Customer": 68},
             "strengths": ["Battery-swap infrastructure differentiation", "Premium brand positioning in China", "Strong owner community loyalty"],
             "weaknesses": ["Persistent cash burn and losses", "Limited presence outside China", "Execution risk on new sub-brands"]},
            {"name": "BYD", "score": 75, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 68, "Innovation": 80, "Leadership": 75, "ESG": 70, "Customer": 72},
             "strengths": ["World's largest EV/PHEV seller by volume", "Vertically integrated battery production", "Aggressive international expansion"],
             "weaknesses": ["Brand perception still building outside China", "Tariff barriers in US/EU markets", "Margin pressure from price wars"]},
            {"name": "Tesla", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 90, "Leadership": 48, "ESG": 60, "Customer": 65},
             "strengths": ["Global brand recognition far exceeds NIO", "Supercharger network moat", "FSD technology lead"],
             "weaknesses": ["CEO controversy drags leadership score", "Inconsistent build quality complaints"]},
            {"name": "XPeng", "score": 54, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 48, "Innovation": 78, "Leadership": 58, "ESG": 62, "Customer": 60},
             "strengths": ["Advanced ADAS/autonomous driving tech", "Strong smart-cockpit software experience", "Volkswagen strategic partnership"],
             "weaknesses": ["Smaller sales volume than NIO/BYD", "Continued profitability challenges", "Brand awareness low outside China"]},
        ]
    },
    "xpeng": {
        "peers": [
            {"name": "XPeng", "score": 54, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 48, "Innovation": 78, "Leadership": 58, "ESG": 62, "Customer": 60},
             "strengths": ["Advanced ADAS/autonomous driving tech", "Strong smart-cockpit software experience", "Volkswagen strategic partnership"],
             "weaknesses": ["Smaller sales volume than BYD/Tesla", "Continued profitability challenges", "Brand awareness low outside China"]},
            {"name": "NIO", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 55, "Innovation": 72, "Leadership": 55, "ESG": 65, "Customer": 68},
             "strengths": ["Battery-swap infrastructure differentiation", "Premium brand positioning in China", "Strong owner community loyalty"],
             "weaknesses": ["Persistent cash burn and losses", "Limited presence outside China", "Execution risk on new sub-brands"]},
            {"name": "BYD", "score": 75, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 68, "Innovation": 80, "Leadership": 75, "ESG": 70, "Customer": 72},
             "strengths": ["World's largest EV/PHEV seller by volume", "Vertically integrated battery production", "Aggressive international expansion"],
             "weaknesses": ["Brand perception still building outside China", "Tariff barriers in US/EU markets", "Margin pressure from price wars"]},
            {"name": "Tesla", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 90, "Leadership": 48, "ESG": 60, "Customer": 65},
             "strengths": ["Global brand recognition far exceeds XPeng", "Supercharger network moat", "FSD technology lead"],
             "weaknesses": ["CEO controversy drags leadership score", "Inconsistent build quality complaints"]},
        ]
    },

    # ─────────────────────────────── BIG TECH ───────────────────────────────
    "microsoft": {
        "peers": [
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Satya Nadella rated best Big Tech CEO", "Copilot AI across entire product suite", "Azure is #2 cloud with fastest growth"],
             "weaknesses": ["Activision integration still uncertain", "Teams NPS trails Slack", "Windows update frustration a perennial issue"]},
            {"name": "Google", "score": 78, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 88, "Leadership": 78, "ESG": 72, "Customer": 68},
             "strengths": ["Workspace dominant in education", "Gemini AI integration speed", "Search monopoly cash engine"],
             "weaknesses": ["Cloud trails Azure & AWS", "Antitrust pressure mounting", "Workspace enterprise sales complex"]},
            {"name": "Amazon", "score": 69, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 80, "Innovation": 75, "Leadership": 70, "ESG": 58, "Customer": 72},
             "strengths": ["AWS is #1 cloud provider by revenue", "Prime ecosystem loyalty", "Bedrock AI platform growing fast"],
             "weaknesses": ["ESG/worker treatment controversy", "Alexa AI behind competitors", "Retail margins thin"]},
        ]
    },
    "google": {
        "peers": [
            {"name": "Google", "score": 78, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 88, "Leadership": 78, "ESG": 72, "Customer": 68},
             "strengths": ["Search + YouTube = unmatched distribution", "Gemini Ultra leading multimodal", "DeepMind research credibility"],
             "weaknesses": ["Privacy concerns persistent", "Antitrust cases in US & EU", "Gemini launch optics hurt AI narrative"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["CEO perception best in Big Tech", "OpenAI investment first-mover", "Enterprise AI rollout fastest"],
             "weaknesses": ["Bing AI market share still small", "Consumer excitement lower", "Gaming bet uncertain"]},
            {"name": "Meta", "score": 55, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 55, "ESG": 42, "Customer": 50},
             "strengths": ["Llama open-source AI developer love", "WhatsApp 2B+ users", "Threads growing fast"],
             "weaknesses": ["Privacy scandal legacy still hurts", "Metaverse pivot scepticism", "Youth trust deficit"]},
        ]
    },
    "amazon": {
        "peers": [
            {"name": "Amazon", "score": 69, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 82, "Innovation": 78, "Leadership": 70, "ESG": 55, "Customer": 72},
             "strengths": ["AWS #1 cloud by revenue & mindshare", "Prime loyalty unmatched in e-commerce", "Bedrock AI growing enterprise traction"],
             "weaknesses": ["Worker treatment ESG controversy", "Alexa falling behind in AI race", "Retail business margin pressure"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Azure AI fastest enterprise rollout", "CEO trusted most in Big Tech", "GitHub Copilot developer love"],
             "weaknesses": ["Cloud #2 behind AWS in revenue", "Consumer product excitement lower", "Activision ROI uncertain"]},
            {"name": "Shopify", "score": 65, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 72, "Leadership": 75, "ESG": 65, "Customer": 80},
             "strengths": ["Merchant NPS highest in e-commerce", "SMB brand champion", "AI commerce tools leading"],
             "weaknesses": ["Much smaller scale than Amazon", "Enterprise tier still building", "Logistics network nascent"]},
        ]
    },
    "meta": {
        "peers": [
            {"name": "Meta", "score": 55, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 55, "ESG": 42, "Customer": 50},
             "strengths": ["3B+ daily users across apps", "Llama 3 best open-source model", "Instagram Reels monetisation"],
             "weaknesses": ["Zuckerberg trust score lowest in Big Tech", "Teen mental health controversy", "Metaverse write-off perception"]},
            {"name": "Snap", "score": 50, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 55, "Innovation": 65, "Leadership": 48, "ESG": 55, "Customer": 52},
             "strengths": ["AR lenses innovation leader", "Gen Z engagement strong", "Spotlight growing"],
             "weaknesses": ["Revenue growth stalled", "Advertiser confidence low", "Daily active user plateau"]},
            {"name": "TikTok", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 72, "Innovation": 80, "Leadership": 40, "ESG": 38, "Customer": 65},
             "strengths": ["Highest engagement rates of any platform", "Algorithm best in class", "Creator economy leader"],
             "weaknesses": ["US/EU ban risk (ByteDance)", "Data privacy controversy", "Brand safety concerns for advertisers"]},
        ]
    },

    # ─────────────────────────────── ENTERPRISE SAAS ───────────────────────────────
    "oracle": {
        "peers": [
            {"name": "Oracle", "score": 70, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 68, "Innovation": 70, "Leadership": 72, "ESG": 60, "Customer": 62},
             "strengths": ["OCI cloud growing fast on AI training demand", "Deep enterprise database entrenchment", "Large-scale AI infrastructure deals"],
             "weaknesses": ["Legacy licensing model seen as outdated", "Customer satisfaction trails newer cloud rivals", "Complex, sales-heavy go-to-market"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Azure AI fastest enterprise rollout", "CEO trusted most in Big Tech", "Broadest enterprise software suite"],
             "weaknesses": ["Cloud pricing complexity criticized", "Teams NPS trails Slack", "Windows update frustration"]},
            {"name": "Salesforce", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 74, "Leadership": 70, "ESG": 75, "Customer": 68},
             "strengths": ["#1 CRM market share globally", "Agentforce AI agent push", "Strong ESG/Trailhead community reputation"],
             "weaknesses": ["Growth deceleration vs earlier years", "Product sprawl complexity for buyers", "Pricing seen as high by SMBs"]},
            {"name": "SAP", "score": 68, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 65, "Leadership": 70, "ESG": 68, "Customer": 60},
             "strengths": ["Dominant ERP incumbent in large enterprises", "Deep vertical industry expertise", "Strong European enterprise trust"],
             "weaknesses": ["Cloud migration (RISE) slower than rivals", "Complex, costly implementations", "Innovation perception trails US rivals"]},
        ]
    },
    "salesforce": {
        "peers": [
            {"name": "Salesforce", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 74, "Leadership": 70, "ESG": 75, "Customer": 68},
             "strengths": ["#1 CRM market share globally", "Agentforce AI agent push", "Strong ESG/Trailhead community reputation"],
             "weaknesses": ["Growth deceleration vs earlier years", "Product sprawl complexity for buyers", "Pricing seen as high by SMBs"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Dynamics 365 bundled with Office/Teams", "Copilot AI integration across suite", "CEO trusted most in Big Tech"],
             "weaknesses": ["CRM historically secondary to core suite", "Teams NPS trails Slack", "Windows update frustration"]},
            {"name": "Oracle", "score": 70, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 68, "Innovation": 70, "Leadership": 72, "ESG": 60, "Customer": 62},
             "strengths": ["Deep enterprise database/ERP entrenchment", "Large-scale AI infrastructure investments", "Broad applications portfolio"],
             "weaknesses": ["Legacy licensing model seen as outdated", "Customer satisfaction trails newer rivals", "Complex go-to-market"]},
            {"name": "ServiceNow", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 60, "Innovation": 78, "Leadership": 75, "ESG": 68, "Customer": 72},
             "strengths": ["Dominant workflow automation platform in IT", "Fast AI agent adoption in enterprise ops", "High customer retention and NPS"],
             "weaknesses": ["Lower brand recognition outside enterprise IT", "Premium pricing limits SMB reach", "Narrower product scope than Salesforce"]},
        ]
    },
    "adobe": {
        "peers": [
            {"name": "Adobe", "score": 73, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 82, "Innovation": 78, "Leadership": 75, "ESG": 70, "Customer": 65},
             "strengths": ["Creative Cloud near-monopoly among professionals", "Firefly generative AI integrated across apps", "Strong subscription revenue retention"],
             "weaknesses": ["Canva eroding entry-level creative market", "Figma acquisition blocked by regulators", "Pricing complaints from SMB creators"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Designer/Copilot creative tools bundled with Office", "Massive existing enterprise distribution", "CEO trusted most in Big Tech"],
             "weaknesses": ["Creative tools less specialized than Adobe's", "Professional creative mindshare still trails Adobe", "Design tool brand less iconic"]},
            {"name": "Salesforce", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 74, "Leadership": 70, "ESG": 75, "Customer": 68},
             "strengths": ["Marketing Cloud competes at the CMO level", "Strong enterprise customer relationships", "Broad SaaS ecosystem"],
             "weaknesses": ["No dedicated creative-tools product line", "Product sprawl complexity for buyers", "Pricing seen as high by SMBs"]},
            {"name": "Canva", "score": 62, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 70, "ESG": 65, "Customer": 78},
             "strengths": ["Beloved by non-professional/SMB creators", "Freemium model drives massive adoption", "Fast AI feature rollout"],
             "weaknesses": ["Less powerful for professional-grade work", "Smaller enterprise sales motion", "Still building brand trust at scale"]},
        ]
    },
    "servicenow": {
        "peers": [
            {"name": "ServiceNow", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 60, "Innovation": 78, "Leadership": 75, "ESG": 68, "Customer": 72},
             "strengths": ["Dominant workflow automation platform in IT", "Fast AI agent adoption in enterprise ops", "High customer retention and NPS"],
             "weaknesses": ["Lower brand recognition outside enterprise IT", "Premium pricing limits SMB reach", "Reliant on continued enterprise IT spend"]},
            {"name": "Salesforce", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 74, "Leadership": 70, "ESG": 75, "Customer": 68},
             "strengths": ["#1 CRM market share globally", "Broader product suite beyond IT workflows", "Strong ESG/Trailhead community reputation"],
             "weaknesses": ["Growth deceleration vs earlier years", "Product sprawl complexity for buyers", "Pricing seen as high by SMBs"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Copilot integration across IT/ops tools", "Massive existing enterprise distribution", "CEO trusted most in Big Tech"],
             "weaknesses": ["IT workflow tools less specialized than ServiceNow's", "Teams NPS trails Slack", "Windows update frustration"]},
            {"name": "Oracle", "score": 70, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 68, "Innovation": 70, "Leadership": 72, "ESG": 60, "Customer": 62},
             "strengths": ["Deep enterprise database/ERP entrenchment", "Large-scale AI infrastructure investments", "Broad applications portfolio"],
             "weaknesses": ["Legacy licensing model seen as outdated", "Customer satisfaction trails newer cloud rivals", "Complex, sales-heavy go-to-market"]},
        ]
    },
    "snowflake": {
        "peers": [
            {"name": "Snowflake", "score": 66, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 76, "Leadership": 65, "ESG": 62, "Customer": 70},
             "strengths": ["Cloud-agnostic data warehouse leader", "Strong developer/analyst community trust", "Expanding into AI/ML workloads (Cortex)"],
             "weaknesses": ["Intensifying competition from Databricks", "Consumption pricing can spike unpredictably", "Leadership transition scrutiny"]},
            {"name": "Databricks", "score": 69, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 50, "Innovation": 82, "Leadership": 75, "ESG": 64, "Customer": 70},
             "strengths": ["Lakehouse architecture popular with data teams", "Strong open-source roots (Spark, MLflow)", "High-profile AI/ML enterprise wins"],
             "weaknesses": ["Still private, valuation scrutiny", "Smaller ecosystem than hyperscaler-native tools", "Competing directly with cloud providers' own tools"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Fabric/Synapse bundled with Azure ecosystem", "CEO trusted most in Big Tech", "Broadest enterprise distribution"],
             "weaknesses": ["Perceived as less cloud-agnostic", "Data platform seen as more complex", "Windows update frustration unrelated legacy issue"]},
            {"name": "Oracle", "score": 70, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 68, "Innovation": 70, "Leadership": 72, "ESG": 60, "Customer": 62},
             "strengths": ["Deep enterprise database entrenchment", "Large-scale AI infrastructure deals", "Broad applications portfolio"],
             "weaknesses": ["Legacy licensing model seen as outdated", "Customer satisfaction trails newer cloud rivals", "Complex go-to-market"]},
        ]
    },
    "databricks": {
        "peers": [
            {"name": "Databricks", "score": 69, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 50, "Innovation": 82, "Leadership": 75, "ESG": 64, "Customer": 70},
             "strengths": ["Lakehouse architecture popular with data teams", "Strong open-source roots (Spark, MLflow)", "High-profile AI/ML enterprise wins"],
             "weaknesses": ["Still private, valuation scrutiny", "Smaller ecosystem than hyperscaler-native tools", "Competing directly with cloud providers' own tools"]},
            {"name": "Snowflake", "score": 66, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 76, "Leadership": 65, "ESG": 62, "Customer": 70},
             "strengths": ["Cloud-agnostic data warehouse leader", "Simpler SQL-first user experience", "Expanding into AI/ML workloads (Cortex)"],
             "weaknesses": ["Intensifying competition from Databricks", "Consumption pricing can spike unpredictably", "Leadership transition scrutiny"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Deep Azure partnership co-sells Databricks", "Fabric offers a competing native alternative", "CEO trusted most in Big Tech"],
             "weaknesses": ["Fabric still maturing vs Databricks", "Perceived as less open-source friendly", "Complex multi-product overlap"]},
            {"name": "Google", "score": 78, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 88, "Leadership": 78, "ESG": 72, "Customer": 68},
             "strengths": ["BigQuery a strong competing data platform", "Deep AI/ML research credibility", "Search monopoly cash engine"],
             "weaknesses": ["Cloud trails Azure & AWS in enterprise share", "Antitrust pressure mounting", "Less lakehouse-native architecture"]},
        ]
    },

    # ─────────────────────────────── SOCIAL / MEDIA ───────────────────────────────
    "tiktok": {
        "peers": [
            {"name": "TikTok", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 72, "Innovation": 80, "Leadership": 40, "ESG": 38, "Customer": 65},
             "strengths": ["Highest engagement rates of any platform", "Algorithm best in class", "Creator economy leader"],
             "weaknesses": ["US/EU ban risk (ByteDance)", "Data privacy controversy", "Brand safety concerns for advertisers"]},
            {"name": "Meta", "score": 55, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 55, "ESG": 42, "Customer": 50},
             "strengths": ["Reels directly competes across Instagram/Facebook", "3B+ daily users across apps", "No comparable geopolitical ban risk"],
             "weaknesses": ["Zuckerberg trust score lowest in Big Tech", "Teen mental health controversy", "Metaverse write-off perception"]},
            {"name": "Snap", "score": 50, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 55, "Innovation": 65, "Leadership": 48, "ESG": 55, "Customer": 52},
             "strengths": ["AR lenses innovation leader", "Gen Z engagement strong", "Spotlight growing"],
             "weaknesses": ["Revenue growth stalled", "Advertiser confidence low", "Daily active user plateau"]},
            {"name": "YouTube", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 82, "Innovation": 78, "Leadership": 75, "ESG": 65, "Customer": 72},
             "strengths": ["Shorts scaled to rival TikTok's reach", "Owned by Google with deep AI integration", "Largest video-creator monetisation program"],
             "weaknesses": ["Shorts still seen as less culturally dominant", "Content moderation criticism", "Ad-load complaints from viewers"]},
        ]
    },
    "reddit": {
        "peers": [
            {"name": "Reddit", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 60, "Leadership": 58, "ESG": 55, "Customer": 62},
             "strengths": ["Highly engaged niche communities (subreddits)", "Valuable human-generated data for AI licensing deals", "Strong organic search/SEO presence"],
             "weaknesses": ["Moderation and content quality inconsistency", "Ad revenue lags larger platforms", "API pricing controversy hurt developer trust"]},
            {"name": "Meta", "score": 55, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 55, "ESG": 42, "Customer": 50},
             "strengths": ["Vastly larger scale across Facebook Groups/Threads", "3B+ daily users across apps", "Stronger ad-tech infrastructure"],
             "weaknesses": ["Community depth seen as shallower than Reddit's", "Teen mental health controversy", "Youth trust deficit"]},
            {"name": "Discord", "score": 60, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 58, "Innovation": 68, "Leadership": 60, "ESG": 52, "Customer": 75},
             "strengths": ["Deeply loyal gaming and creator communities", "Strong real-time voice/video engagement", "High customer satisfaction"],
             "weaknesses": ["Monetization still developing (Nitro-dependent)", "Content moderation and safety scrutiny", "Not yet profitable at scale"]},
            {"name": "TikTok", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 72, "Innovation": 80, "Leadership": 40, "ESG": 38, "Customer": 65},
             "strengths": ["Far higher engagement and cultural relevance", "Best-in-class recommendation algorithm", "Creator economy leader"],
             "weaknesses": ["US/EU ban risk (ByteDance)", "Data privacy controversy", "Brand safety concerns for advertisers"]},
        ]
    },
    "linkedin": {
        "peers": [
            {"name": "LinkedIn", "score": 70, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 65, "Leadership": 75, "ESG": 72, "Customer": 68},
             "strengths": ["Dominant professional networking platform", "Owned by Microsoft with deep enterprise ties", "Strong recruiting/talent-solutions revenue"],
             "weaknesses": ["Feed engagement lower than consumer social apps", "Perceived as less fun/casual by younger users", "Premium subscription value questioned by some"]},
            {"name": "Meta", "score": 55, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 55, "ESG": 42, "Customer": 50},
             "strengths": ["Vastly larger overall user base", "Stronger ad-tech and targeting", "Faster feature iteration"],
             "weaknesses": ["No dedicated professional-networking product", "Teen mental health controversy", "Youth trust deficit"]},
            {"name": "TikTok", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 72, "Innovation": 80, "Leadership": 40, "ESG": 38, "Customer": 65},
             "strengths": ["Far higher engagement among younger professionals", "Best-in-class recommendation algorithm", "Creator economy leader"],
             "weaknesses": ["US/EU ban risk (ByteDance)", "Not built for professional networking", "Brand safety concerns for advertisers"]},
            {"name": "Reddit", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 60, "Leadership": 58, "ESG": 55, "Customer": 62},
             "strengths": ["Deep niche professional/industry communities", "Valuable data for AI licensing deals", "Strong organic search presence"],
             "weaknesses": ["Not identity-verified/professional by design", "Ad revenue lags larger platforms", "API pricing controversy hurt developer trust"]},
        ]
    },
    "discord": {
        "peers": [
            {"name": "Discord", "score": 60, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 58, "Innovation": 68, "Leadership": 60, "ESG": 52, "Customer": 75},
             "strengths": ["Deeply loyal gaming and creator communities", "Strong real-time voice/video engagement", "Expanding beyond gaming into general community use"],
             "weaknesses": ["Monetization still developing (Nitro-dependent)", "Content moderation and safety scrutiny", "Not yet profitable at scale"]},
            {"name": "Reddit", "score": 58, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 60, "Leadership": 58, "ESG": 55, "Customer": 62},
             "strengths": ["Highly engaged niche communities (subreddits)", "Valuable human-generated data for AI licensing deals", "Strong organic search/SEO presence"],
             "weaknesses": ["Moderation and content quality inconsistency", "Ad revenue lags larger platforms", "API pricing controversy hurt developer trust"]},
            {"name": "TikTok", "score": 52, "grade": "Fair", "risk": "High",
             "dims": {"Brand": 72, "Innovation": 80, "Leadership": 40, "ESG": 38, "Customer": 65},
             "strengths": ["Far higher mainstream engagement", "Best-in-class recommendation algorithm", "Creator economy leader"],
             "weaknesses": ["US/EU ban risk (ByteDance)", "Data privacy controversy", "Brand safety concerns for advertisers"]},
            {"name": "Meta", "score": 55, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 60, "Innovation": 75, "Leadership": 55, "ESG": 42, "Customer": 50},
             "strengths": ["Vastly larger scale via Messenger/WhatsApp", "Stronger ad-tech infrastructure", "3B+ daily users across apps"],
             "weaknesses": ["Community depth seen as shallower than Discord's", "Teen mental health controversy", "Youth trust deficit"]},
        ]
    },
    "spotify": {
        "peers": [
            {"name": "Spotify", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 78, "Innovation": 70, "Leadership": 75, "ESG": 65, "Customer": 75},
             "strengths": ["#1 global music streaming market share", "Strong podcast ecosystem investment", "Personalization/algorithm engagement leader"],
             "weaknesses": ["Thin margins on music licensing costs", "Increasing competition from Apple/Amazon bundles", "Artist payout criticism"]},
            {"name": "Apple", "score": 85, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 98, "Innovation": 82, "Leadership": 88, "ESG": 80, "Customer": 90},
             "strengths": ["Apple Music bundled into wider ecosystem", "Premium brand loyalty across hardware", "Strong device integration advantage"],
             "weaknesses": ["Music discovery/personalization trails Spotify", "Smaller standalone music market share", "Less podcast-specific investment"]},
            {"name": "Amazon", "score": 69, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 82, "Innovation": 78, "Leadership": 70, "ESG": 58, "Customer": 72},
             "strengths": ["Music bundled free with Prime membership", "Massive existing subscriber base", "Alexa voice integration"],
             "weaknesses": ["Music seen as a Prime perk, not standalone leader", "Alexa AI behind competitors", "Retail-first brand identity"]},
            {"name": "YouTube", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 82, "Innovation": 78, "Leadership": 75, "ESG": 65, "Customer": 72},
             "strengths": ["YouTube Music leverages massive video catalog", "Owned by Google with deep AI integration", "Strong free ad-supported tier"],
             "weaknesses": ["Music app seen as secondary to video product", "Content moderation criticism", "Less curated music-discovery brand"]},
        ]
    },
    "netflix": {
        "peers": [
            {"name": "Netflix", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 85, "Innovation": 75, "Leadership": 80, "ESG": 68, "Customer": 78},
             "strengths": ["Largest global streaming subscriber base", "Strong original content production engine", "Ad-tier driving new subscriber growth"],
             "weaknesses": ["Content costs remain very high", "Password-sharing crackdown backlash", "Intensifying competition fragmenting the market"]},
            {"name": "Disney+", "score": 65, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 88, "Innovation": 65, "Leadership": 68, "ESG": 65, "Customer": 68},
             "strengths": ["Unmatched franchise IP library (Marvel, Star Wars, Pixar)", "Strong family-audience brand trust", "Bundling with Hulu/ESPN"],
             "weaknesses": ["Streaming division profitability still uneven", "Content output smaller than Netflix's", "Subscriber growth slower than Netflix"]},
            {"name": "Amazon", "score": 69, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 82, "Innovation": 78, "Leadership": 70, "ESG": 58, "Customer": 72},
             "strengths": ["Prime Video bundled with broader Prime membership", "Massive existing subscriber base", "Growing live-sports rights portfolio"],
             "weaknesses": ["Original content seen as less consistent than Netflix's", "Video seen as a Prime perk, not standalone leader", "Retail margins thin"]},
            {"name": "YouTube", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 82, "Innovation": 78, "Leadership": 75, "ESG": 65, "Customer": 72},
             "strengths": ["Largest free video library on earth", "Owned by Google with deep AI integration", "Strong creator-economy monetisation"],
             "weaknesses": ["Less premium scripted-content brand than Netflix", "Content moderation criticism", "Ad-load complaints from viewers"]},
        ]
    },

    # ─────────────────────────────── INDIA / IT SERVICES ───────────────────────────────
    "reliance_jio": {
        "peers": [
            {"name": "Reliance Jio", "score": 74, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 72, "Leadership": 78, "ESG": 60, "Customer": 70},
             "strengths": ["#1 telecom operator in India by subscribers", "Aggressive 5G rollout and digital ecosystem", "Backed by Reliance Industries' scale"],
             "weaknesses": ["Heavy capex burden on parent balance sheet", "ARPU still low versus global telecoms", "Regulatory environment complexity"]},
            {"name": "TCS", "score": 73, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 68, "Leadership": 78, "ESG": 70, "Customer": 72},
             "strengths": ["Largest Indian IT services firm by revenue", "Strong long-term enterprise client relationships", "High employee retention vs industry"],
             "weaknesses": ["Growth slowing amid global IT spending caution", "Perceived as less innovative than boutique AI firms", "Heavy reliance on US/UK client markets"]},
            {"name": "Infosys", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 70, "Leadership": 75, "ESG": 72, "Customer": 70},
             "strengths": ["Strong digital transformation consulting reputation", "Topaz AI platform enterprise traction", "Consistent margin discipline"],
             "weaknesses": ["Client concentration in BFSI/retail sectors", "Attrition volatility in past cycles", "Trails TCS in overall scale"]},
        ]
    },
    "tcs": {
        "peers": [
            {"name": "TCS", "score": 73, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 68, "Leadership": 78, "ESG": 70, "Customer": 72},
             "strengths": ["Largest Indian IT services firm by revenue", "Strong long-term enterprise client relationships", "High employee retention vs industry"],
             "weaknesses": ["Growth slowing amid global IT spending caution", "Perceived as less innovative than boutique AI firms", "Heavy reliance on US/UK client markets"]},
            {"name": "Infosys", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 70, "Leadership": 75, "ESG": 72, "Customer": 70},
             "strengths": ["Strong digital transformation consulting reputation", "Topaz AI platform enterprise traction", "Consistent margin discipline"],
             "weaknesses": ["Client concentration in BFSI/retail sectors", "Attrition volatility in past cycles", "Trails TCS in overall scale"]},
            {"name": "Accenture", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 80, "Innovation": 78, "Leadership": 78, "ESG": 74, "Customer": 72},
             "strengths": ["Broadest global consulting + tech brand", "Deep strategy-to-execution capabilities", "Large-scale AI transformation practice"],
             "weaknesses": ["Higher price points than Indian IT peers", "Margins thinner on large complex projects", "Bench/utilization pressure in slow markets"]},
            {"name": "Wipro", "score": 62, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 62, "Leadership": 65, "ESG": 68, "Customer": 60},
             "strengths": ["Broad services portfolio across verticals", "Growing cloud & AI practice", "Long-standing client relationships"],
             "weaknesses": ["Growth trails TCS/Infosys", "Brand recognition lower globally", "Margin pressure from pricing competition"]},
        ]
    },
    "infosys": {
        "peers": [
            {"name": "Infosys", "score": 71, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 65, "Innovation": 70, "Leadership": 75, "ESG": 72, "Customer": 70},
             "strengths": ["Strong digital transformation consulting reputation", "Topaz AI platform enterprise traction", "Consistent margin discipline"],
             "weaknesses": ["Client concentration in BFSI/retail sectors", "Attrition volatility in past cycles", "Trails TCS in overall scale"]},
            {"name": "TCS", "score": 73, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 70, "Innovation": 68, "Leadership": 78, "ESG": 70, "Customer": 72},
             "strengths": ["Largest Indian IT services firm by revenue", "Strong long-term enterprise client relationships", "High employee retention vs industry"],
             "weaknesses": ["Growth slowing amid global IT spending caution", "Perceived as less innovative than boutique AI firms", "Heavy reliance on US/UK client markets"]},
            {"name": "Accenture", "score": 76, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 80, "Innovation": 78, "Leadership": 78, "ESG": 74, "Customer": 72},
             "strengths": ["Broadest global consulting + tech brand", "Deep strategy-to-execution capabilities", "Large-scale AI transformation practice"],
             "weaknesses": ["Higher price points than Indian IT peers", "Margins thinner on large complex projects", "Bench/utilization pressure in slow markets"]},
            {"name": "Wipro", "score": 62, "grade": "Good", "risk": "Medium",
             "dims": {"Brand": 55, "Innovation": 62, "Leadership": 65, "ESG": 68, "Customer": 60},
             "strengths": ["Broad services portfolio across verticals", "Growing cloud & AI practice", "Long-standing client relationships"],
             "weaknesses": ["Growth trails TCS/Infosys", "Brand recognition lower globally", "Margin pressure from pricing competition"]},
        ]
    },
    "zoho": {
        "peers": [
            {"name": "Zoho", "score": 68, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 50, "Innovation": 70, "Leadership": 80, "ESG": 75, "Customer": 78},
             "strengths": ["Profitable, bootstrapped business model rarity", "Broad SaaS suite at SMB-friendly pricing", "Strong founder-led long-term vision"],
             "weaknesses": ["Lower global brand recognition than Salesforce", "Limited enterprise-scale marketing spend", "Smaller ecosystem/integration marketplace"]},
            {"name": "Salesforce", "score": 72, "grade": "Good", "risk": "Low",
             "dims": {"Brand": 75, "Innovation": 74, "Leadership": 70, "ESG": 75, "Customer": 68},
             "strengths": ["#1 CRM market share globally", "Agentforce AI agent push", "Vastly larger marketing and sales reach"],
             "weaknesses": ["Pricing seen as high by SMBs", "Product sprawl complexity for buyers", "Growth deceleration vs earlier years"]},
            {"name": "Microsoft", "score": 82, "grade": "Excellent", "risk": "Low",
             "dims": {"Brand": 88, "Innovation": 84, "Leadership": 90, "ESG": 82, "Customer": 75},
             "strengths": ["Dynamics 365 bundled with Office/Teams", "Copilot AI integration across suite", "CEO trusted most in Big Tech"],
             "weaknesses": ["Less SMB-friendly pricing than Zoho", "Complex licensing for smaller businesses", "Windows update frustration unrelated legacy issue"]},
            {"name": "Freshworks", "score": 60, "grade": "Fair", "risk": "Medium",
             "dims": {"Brand": 48, "Innovation": 68, "Leadership": 65, "ESG": 62, "Customer": 72},
             "strengths": ["Strong SMB/mid-market customer support focus", "Simple, approachable product design", "Fast-growing AI-enabled helpdesk tools"],
             "weaknesses": ["Smaller product suite than Zoho", "Less profitable growth profile", "Lower brand recognition than larger rivals"]},
        ]
    },
}

def get_competitor_data(company_name: str) -> list:
    key = company_name.strip().lower()
    for k, v in COMPETITOR_DB.items():
        if k in key or key in k:
            return v["peers"]
    # Fallback generic
    import random; rng = random.Random(_seed_from(company_name) + 2)
    base = rng.randint(50, 82)
    return [{
        "name": company_name.title(), "score": base,
        "grade": "Good" if base>=70 else "Fair", "risk": "Low" if base>=70 else "Medium",
        "dims": {"Brand":base,"Innovation":base+5,"Leadership":base-5,"ESG":base-10,"Customer":base+8},
        "strengths": ["Market presence", "Product innovation", "Customer loyalty"],
        "weaknesses": ["Brand awareness", "Competition pressure"],
    }]


# ── Competitor HTML components ────────────────────────────────
def competitor_cards_html(peers):
    cards = ""
    for i, p in enumerate(peers):
        score    = p["score"]
        ring_col = "#1DAD85" if score>=70 else "#F0A030" if score>=45 else "#E2504A"
        pct      = max(0, min(score/100, 1))
        circ     = 2*3.14159*22
        dash, gap = pct*circ, (1-pct)*circ
        border   = "#5B52C8" if i==0 else "#182030"
        badge    = ("<div style='font-size:9px;font-weight:700;letter-spacing:.1em;"
                    "color:#5B52C8;text-transform:uppercase;margin-bottom:6px;'>PRIMARY</div>") if i==0 else ""
        cards += f"""
        <div style="flex:1;min-width:150px;background:#0C1120;border:1px solid {border};
             border-radius:14px;padding:18px 20px;">
          {badge}
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <svg width="50" height="50" viewBox="0 0 50 50" style="flex-shrink:0">
              <circle cx="25" cy="25" r="22" fill="none" stroke="#182030" stroke-width="4"/>
              <circle cx="25" cy="25" r="22" fill="none" stroke="{ring_col}" stroke-width="4"
                stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-linecap="round"
                transform="rotate(-90 25 25)"/>
              <text x="25" y="30" text-anchor="middle" font-size="12" font-weight="700"
                fill="#E8EEFF" font-family="DM Mono,monospace">{score}</text>
            </svg>
            <div>
              <div style="font-size:14px;font-weight:700;color:#E8EEFF;">{p['name']}</div>
              <div style="font-size:11px;color:#2E3D58;margin-top:2px;">{p['grade']} · {p['risk']} risk</div>
            </div>
          </div>
          <div style="height:3px;background:#182030;border-radius:2px;overflow:hidden;">
            <div style="height:100%;width:{score}%;background:{ring_col};border-radius:2px;"></div>
          </div>
        </div>"""
    return f"""{_head()}<div style="display:flex;gap:12px;flex-wrap:wrap;">{cards}</div>"""


def competitor_detail_html(peers):
    """Why competitors score the way they do — strengths & weaknesses per company."""
    dims_order = ["Brand","Innovation","Leadership","ESG","Customer"]
    cards = ""
    for i, p in enumerate(peers):
        is_primary = i == 0
        border_left = "border-left:3px solid #5B52C8;" if is_primary else ""
        score    = p["score"]
        ring_col = "#1DAD85" if score>=70 else "#F0A030" if score>=45 else "#E2504A"

        # Dimension bars
        dim_rows = ""
        for dim in dims_order:
            v  = p["dims"].get(dim, score)
            dc = "#1DAD85" if v>=70 else "#F0A030" if v>=45 else "#E2504A"
            dim_rows += f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:7px;">
              <div style="font-size:11px;color:#3A4F6E;width:72px;flex-shrink:0;">{dim}</div>
              <div style="flex:1;height:4px;background:#182030;border-radius:2px;overflow:hidden;">
                <div style="height:100%;width:{v}%;background:{dc};border-radius:2px;"></div>
              </div>
              <div style="font-size:11px;color:#E8EEFF;width:24px;text-align:right;
                   font-family:DM Mono,monospace;">{v}</div>
            </div>"""

        # Strengths
        str_items = "".join(
            f"<div style='display:flex;gap:8px;margin-bottom:5px;font-size:12px;color:#94A3B8;line-height:1.5;'>"
            f"<span style='color:#1DAD85;margin-top:2px;flex-shrink:0;'>✓</span><span>{s}</span></div>"
            for s in p.get("strengths", [])
        )
        # Weaknesses
        weak_items = "".join(
            f"<div style='display:flex;gap:8px;margin-bottom:5px;font-size:12px;color:#94A3B8;line-height:1.5;'>"
            f"<span style='color:#E2504A;margin-top:2px;flex-shrink:0;'>✗</span><span>{w}</span></div>"
            for w in p.get("weaknesses", [])
        )

        primary_tag = ("<span style='font-size:9px;font-weight:700;letter-spacing:.1em;"
                       "color:#5B52C8;text-transform:uppercase;background:rgba(91,82,200,0.12);"
                       "padding:2px 8px;border-radius:10px;margin-left:8px;'>PRIMARY</span>") if is_primary else ""

        cards += f"""
        <div style="background:#0C1120;border:1px solid #182030;{border_left}
             border-radius:16px;padding:22px 24px;margin-bottom:14px;">
          <div style="display:flex;align-items:center;gap:14px;margin-bottom:18px;">
            <svg width="44" height="44" viewBox="0 0 50 50" style="flex-shrink:0">
              <circle cx="25" cy="25" r="22" fill="none" stroke="#182030" stroke-width="4"/>
              <circle cx="25" cy="25" r="22" fill="none" stroke="{ring_col}" stroke-width="4"
                stroke-dasharray="{min(score,100)/100*2*3.14159*22:.1f} 999"
                stroke-linecap="round" transform="rotate(-90 25 25)"/>
              <text x="25" y="30" text-anchor="middle" font-size="12" font-weight="700"
                fill="#E8EEFF" font-family="DM Mono,monospace">{score}</text>
            </svg>
            <div>
              <div style="font-size:16px;font-weight:700;color:#E8EEFF;">{p['name']}{primary_tag}</div>
              <div style="font-size:11px;color:#2E3D58;margin-top:3px;">{p['grade']} grade · {p['risk']} risk</div>
            </div>
          </div>
          <div style="margin-bottom:16px;">{dim_rows}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div>
              <div style="font-size:10px;font-weight:700;letter-spacing:.12em;color:#1DAD85;
                   text-transform:uppercase;margin-bottom:8px;">Why they score well</div>
              {str_items}
            </div>
            <div>
              <div style="font-size:10px;font-weight:700;letter-spacing:.12em;color:#E2504A;
                   text-transform:uppercase;margin-bottom:8px;">Where they fall short</div>
              {weak_items}
            </div>
          </div>
        </div>"""

    return f"""{_head()}<div>{cards}</div>"""


def anomaly_alert_html(events):
    if not events:
        return None
    items = ""
    for e in events[:5]:
        is_spike = e["dir"] == "spike"
        bg  = "rgba(226,80,74,0.08)"  if is_spike else "rgba(240,160,48,0.08)"
        bc  = "rgba(226,80,74,0.22)"  if is_spike else "rgba(240,160,48,0.22)"
        dot = "#E2504A" if is_spike else "#F0A030"
        col = "#F08080" if is_spike else "#EFBF27"
        arrow = "▲" if is_spike else "▼"
        label = "Spike" if is_spike else "Drop"
        items += f"""
        <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;
             border-radius:10px;margin-bottom:8px;font-size:12.5px;line-height:1.5;
             background:{bg};border:1px solid {bc};color:#94A3B8;">
          <div style="width:7px;height:7px;border-radius:50%;background:{dot};margin-top:5px;flex-shrink:0;"></div>
          <div>
            <strong style="color:{col};">{arrow} {label} — {e['date']}</strong><br>
            {e['value']:,} mentions &nbsp;·&nbsp; {e['pct_dev']}% above normal &nbsp;·&nbsp;
            z-score <span style="font-family:DM Mono,monospace;">{e['z']}</span>
          </div>
        </div>"""
    return f"""{_head()}
<div style="background:#0C1120;border:1px solid #182030;border-radius:16px;padding:22px 24px;">
  <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;
       text-transform:uppercase;margin-bottom:14px;">🔍 Anomaly detection</div>
  {items}
</div>"""

def timeline_events_html(events):
    if not events:
        return None
    items = ""
    for e in sorted(events, key=lambda x: x["date"]):
        is_neg  = e["delta"] < 0
        dot_col = "#E2504A" if is_neg else "#1DAD85"
        dlt_col = "#F08080" if is_neg else "#4EC9A0"
        arrow   = "▼" if is_neg else "▲"
        items += f"""
        <div style="display:flex;gap:14px;padding:10px 0;border-bottom:1px solid #131E34;">
          <div style="display:flex;flex-direction:column;align-items:center;">
            <div style="width:8px;height:8px;border-radius:50%;background:{dot_col};margin-top:4px;flex-shrink:0;"></div>
            <div style="flex:1;width:1px;background:#182030;margin-top:4px;"></div>
          </div>
          <div style="flex:1;padding-bottom:4px;">
            <div style="font-size:11px;color:#3A4F6E;margin-bottom:3px;">{e['date']}</div>
            <div style="font-size:13px;color:#E8EEFF;font-weight:600;">{e['label']}</div>
            <div style="font-size:12px;color:{dlt_col};margin-top:2px;">
              {arrow} {abs(e['delta'])} pts &nbsp;·&nbsp;
              Score: <span style="font-family:DM Mono,monospace;">{e['score']}</span>
            </div>
          </div>
        </div>"""
    return f"""{_head()}
<div style="background:#0C1120;border:1px solid #182030;border-radius:16px;padding:20px 24px;">
  <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;
       text-transform:uppercase;margin-bottom:14px;">📅 Event log</div>
  {items}
</div>"""


# ── Synthetic data helpers ────────────────────────────────────
def _seed_from(name):
    return int(hashlib.md5(name.lower().encode()).hexdigest()[:8], 16)

def make_stakeholder_scores(score, seed):
    import random; rng = random.Random(seed)
    return {
        "Customers": max(10, min(100, score + rng.randint(15,25))),
        "Investors":  max(10, min(100, score + rng.randint(-10,5))),
        "Media":      max(10, min(100, score + rng.randint(5,18))),
        "Employees":  max(10, min(100, score + rng.randint(-5,12))),
    }

def make_velocity_history(score, seed):
    import random; rng = random.Random(seed + 1)
    base  = max(20, 120 - score)
    dates = [(datetime.now() - timedelta(days=29-i)).strftime("%b %d") for i in range(30)]
    vals  = [max(5, base + rng.randint(-20,40)) for _ in range(30)]
    return pd.DataFrame({"date": dates, "mentions": vals})

def detect_anomalies(df, col="mentions", window=7, z_thresh=2.0):
    df = df.copy()
    df["rolling_mean"] = df[col].rolling(window, min_periods=1).mean()
    df["rolling_std"]  = df[col].rolling(window, min_periods=1).std().fillna(1)
    df["z_score"]      = (df[col] - df["rolling_mean"]) / df["rolling_std"]
    df["is_anomaly"]   = df["z_score"].abs() >= z_thresh
    df["anomaly_dir"]  = df["z_score"].apply(
        lambda z: "spike" if z >= z_thresh else "drop" if z <= -z_thresh else "normal"
    )
    return df

def anomaly_summary(df):
    events = []
    for _, row in df[df["is_anomaly"]].iterrows():
        events.append({
            "date":    row["date"],
            "value":   int(row["mentions"]),
            "z":       round(float(row["z_score"]), 1),
            "dir":     row["anomaly_dir"],
            "pct_dev": min(int(abs(row["z_score"]) / 2.0 * 100), 999),
        })
    return sorted(events, key=lambda x: -abs(x["z"]))

def anomaly_chart(df, col="mentions", line_color="#5B52C8", key="anomaly"):
    spikes = df[df["anomaly_dir"] == "spike"]
    drops  = df[df["anomaly_dir"] == "drop"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(df["date"]) + list(df["date"])[::-1],
        y=list(df["rolling_mean"] + 1.5*df["rolling_std"]) +
          list((df["rolling_mean"] - 1.5*df["rolling_std"]).clip(lower=0))[::-1],
        fill="toself", fillcolor="rgba(91,82,200,0.07)",
        line=dict(color="rgba(0,0,0,0)"), name="Normal band", showlegend=False,
    ))
    fig.add_trace(go.Scatter(x=df["date"], y=df[col], mode="lines", name="Mentions",
                             line=dict(color=line_color, width=2)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["rolling_mean"], mode="lines",
                             name="7-day avg", line=dict(color="#3A4F6E", width=1, dash="dot")))
    if len(spikes):
        fig.add_trace(go.Scatter(x=spikes["date"], y=spikes[col], mode="markers", name="Spike",
                                 marker=dict(color="#E2504A", size=10, symbol="triangle-up",
                                             line=dict(color="#FF8080", width=1.5))))
    if len(drops):
        fig.add_trace(go.Scatter(x=drops["date"], y=drops[col], mode="markers", name="Drop",
                                 marker=dict(color="#F0A030", size=10, symbol="triangle-down",
                                             line=dict(color="#FFD080", width=1.5))))
    fig.update_layout(
        **CHART_LAYOUT, height=320,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B"), orientation="h", y=-0.2),
    )
    return fig

def build_timeline(company_name, current_score, seed):
    hist_path = Path("data/history/reputation_history.csv")
    if hist_path.exists():
        df = pd.read_csv(hist_path)
        if len(df) >= 7 and "reputation_score" in df.columns:
            df = df.tail(90).copy()
            if "date" not in df.columns:
                df["date"] = pd.date_range(end=datetime.now(), periods=len(df), freq="D").strftime("%b %d")
            df["delta"] = df["reputation_score"].diff().fillna(0)
            events = []
            for _, row in df[df["delta"].abs() >= 5].iterrows():
                events.append({"date": row["date"], "score": int(row["reputation_score"]),
                                "delta": int(row["delta"]),
                                "label": "Score drop" if row["delta"] < 0 else "Score rise"})
            return df, events

    import random; rng = random.Random(seed + 99)
    s = max(20, min(90, current_score + rng.randint(-8, 8)))
    dates, scores = [], []
    for i in range(90):
        dates.append((datetime.now() - timedelta(days=89-i)).strftime("%b %d"))
        shock = rng.randint(-12,12) if rng.random() < 0.12 else rng.randint(-3,3)
        s = max(10, min(100, s + shock))
        scores.append(s)
    df = pd.DataFrame({"date": dates, "reputation_score": scores})
    df["delta"] = df["reputation_score"].diff().fillna(0)

    neg_labels = ["CEO controversy","Negative press coverage","Product recall rumour","Data breach report","Earnings miss"]
    pos_labels = ["Record results","Product launch","Positive analyst upgrade","Partnership announced","Award received"]
    events = []
    for _, row in df[df["delta"].abs() >= 7].head(5).iterrows():
        pool = neg_labels if row["delta"] < 0 else pos_labels
        events.append({"date": row["date"], "score": int(row["reputation_score"]),
                       "delta": int(row["delta"]), "label": pool[rng.randint(0, len(pool)-1)]})
    return df, events

def timeline_chart(df, events, company):
    event_dates  = [e["date"]  for e in events]
    event_scores = [e["score"] for e in events]
    event_labels = [e["label"] for e in events]
    event_deltas = [e["delta"] for e in events]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["reputation_score"],
                             mode="lines", fill="tozeroy",
                             fillcolor="rgba(91,82,200,0.07)",
                             line=dict(color="#5B52C8", width=2), name="Reputation score"))
    if events:
        marker_colors = ["#E2504A" if d < 0 else "#1DAD85" for d in event_deltas]
        fig.add_trace(go.Scatter(
            x=event_dates, y=event_scores, mode="markers+text",
            marker=dict(color=marker_colors, size=11, symbol="circle",
                        line=dict(color="#E8EEFF", width=1.5)),
            text=[f"  {l}" for l in event_labels],
            textposition="top right", textfont=dict(color="#94A3B8", size=10),
            name="Events",
            hovertext=[f"{l}<br>Score:{s}<br>Δ{d:+d}" for l,s,d in
                       zip(event_labels, event_scores, event_deltas)],
            hoverinfo="text",
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#64748B", size=12),
        margin=dict(l=0, r=0, t=36, b=0),
        xaxis=dict(gridcolor="#131E34", linecolor="#131E34", tickfont=dict(color="#64748B")),
        yaxis=dict(range=[0,105], gridcolor="#131E34", linecolor="#131E34", tickfont=dict(color="#64748B")),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B"), orientation="h", y=-0.2),
        height=360,
    )
    return fig


# ── PDF export ────────────────────────────────────────────────
def generate_pdf(company, score, grade, risk, top_issue):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter,
                                leftMargin=.85*inch, rightMargin=.85*inch,
                                topMargin=.85*inch, bottomMargin=.85*inch)
        styles = getSampleStyleSheet()
        def ps(base, **kw): return ParagraphStyle(base+"_c", parent=styles[base], **kw)
        accent = colors.HexColor("#5B52C8"); dark = colors.HexColor("#1E293B")
        story = [
            Paragraph("🧠 SocialMind AI", ps("Normal", fontSize=9, textColor=accent, spaceAfter=4)),
            Paragraph(f"CEO Briefing — {company}", ps("Title", fontSize=24, textColor=dark, spaceAfter=4)),
            Paragraph(datetime.now().strftime("%B %d, %Y"), ps("Normal", fontSize=10, textColor=colors.HexColor("#64748B"), spaceAfter=16)),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")),
            Spacer(1, 14),
        ]
        tbl = Table([["Reputation Score","Grade","Risk Level","Primary Issue"],
                     [str(score), grade, risk, top_issue[:26]]], colWidths=[1.4*inch]*4)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#F1F5F9")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#475569")),
            ("FONTSIZE",(0,0),(-1,0),8), ("FONTSIZE",(0,1),(-1,1),13),
            ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("BOX",(0,0),(-1,-1),.5,colors.HexColor("#E2E8F0")),
            ("INNERGRID",(0,0),(-1,-1),.3,colors.HexColor("#E2E8F0")),
            ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ]))
        story += [tbl, Spacer(1,18)]
        story.append(Paragraph("Executive Summary", ps("Heading2", textColor=dark, spaceAfter=8)))
        story.append(Paragraph(
            f"Negative discussion is concentrated around <b>{top_issue}</b>. "
            f"Public perception indicates a <b>{risk.lower()} risk</b> environment.",
            ps("Normal", fontSize=11, leading=18, spaceAfter=14)))
        story.append(Paragraph("Recommended Actions", ps("Heading2", textColor=dark, spaceAfter=8)))
        for a in [f"Increase executive transparency on <b>{top_issue.lower()}</b>",
                  "Accelerate internal communications cadence",
                  "Monitor media velocity daily and trigger escalation if risk worsens",
                  "Brief investor relations before next earnings call"]:
            story.append(Paragraph(f"• {a}", ps("Normal", fontSize=11, leading=17, leftIndent=12, spaceAfter=6)))
        story += [Spacer(1,20), HRFlowable(width="100%", thickness=.5, color=colors.HexColor("#E2E8F0")),
                  Paragraph("Generated by SocialMind AI · Confidential",
                             ps("Normal", fontSize=8, textColor=colors.HexColor("#94A3B8"), spaceBefore=8))]
        doc.build(story)
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None


# ── Data loading ──────────────────────────────────────────────
def _find_csv(folder, *candidates):
    for name in candidates:
        p = folder / name
        if p.exists():
            return p
    return None

def check_cached_company(company_name):

    companies_root = Path("data/companies")

    if companies_root.exists():

        for folder in companies_root.iterdir():

            if (
                folder.is_dir()
                and folder.name.lower()
                == company_name.strip().lower()
            ):

                if _find_csv(folder, "company_dataset.csv"):
                    return folder, True

    live = Path("data/live")

    if live.exists():
        return live, False

    return None, False
@st.cache_data(ttl=600, show_spinner=False)
def load_report_data(base_path_str):

    base = Path(base_path_str)

    summary_file = _find_csv(base, "reputation_summary.csv")
    analysis_file = _find_csv(
        base,
        "reputation_analysis.csv",
        "company_dataset.csv"
    )
    issue_file = _find_csv(base, "issue_summary.csv")

    summary = pd.read_csv(summary_file)

    analysis = pd.read_csv(analysis_file)

    issues = pd.read_csv(issue_file)

    analysis.columns = [
        c.lower().strip()
        for c in analysis.columns
    ]

    if "content" in analysis.columns and "text" not in analysis.columns:
        analysis = analysis.rename(
            columns={"content": "text"}
        )

    if "label" in analysis.columns and "sentiment" not in analysis.columns:
        analysis = analysis.rename(
            columns={"label": "sentiment"}
        )

    advisory_path = base / "advisory.json"

    advisory = None

    if advisory_path.exists():

        with open(advisory_path, "r", encoding="utf-8") as f:
            advisory = json.load(f)

    return summary, analysis, issues, advisory

# ── Session state ─────────────────────────────────────────────
for k, v in [("analyzed",False),("company_name",""),("analysis_success",False),("from_cache",False)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ── Landing ───────────────────────────────────────────────────
if not st.session_state.analyzed:
    st.markdown("""
    <div style="text-align:center;padding:5rem 1rem 2.5rem;">
      <div style="font-size:11px;font-weight:700;letter-spacing:.22em;color:#5B52C8;
                  text-transform:uppercase;margin-bottom:1.5rem;">🧠 SocialMind AI</div>
      <div style="font-size:clamp(40px,6vw,64px);font-weight:700;color:#E8EEFF;
                  line-height:1.08;letter-spacing:-0.035em;margin-bottom:1.2rem;">
        Reputation<br><span style="color:#5B52C8;">Intelligence</span>
      </div>
      <div style="font-size:15px;color:#3A4F6E;line-height:1.75;max-width:500px;margin:0 auto 3rem;">
        Monitor public perception, surface emerging risks,<br>
        and brief your leadership — all from a single search.<br>
        <span style="color:#5B52C8;font-size:13px;">Try: ChatGPT · Claude · iPhone · Gemini · Copilot</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="
    text-align:center;
    font-size:13px;
    color:#64748B;
    margin-top:-10px;
    margin-bottom:28px;
    ">

    Designed for
    <strong style="color:#9B8FEE;">
    AI & LLM • Consumer Tech • SaaS • Semiconductor • EV • Social Media
    </strong>

    </div>
""", unsafe_allow_html=True)
    st.markdown("""
    <div style="
    background:rgba(91,82,200,.08);
    border:1px solid rgba(91,82,200,.18);
    border-radius:16px;
    padding:18px 24px;
    margin:20px auto 30px auto;
    max-width:780px;
    ">

    <h3 style="color:#E8EEFF;margin-top:0;">🎯 Project </h3>

    <p style="color:#C9D4F5;">
    <b>SocialMind AI</b> is designed for <b>technology-driven companies</b>.
    It analyzes public perception from <b>News Articles</b>,
    <b>YouTube Videos</b>, and <b>YouTube Comments</b> to generate
    AI-powered reputation intelligence.
    </p>

    <p style="color:#B5C4E0;">
    <b>Supported Industries</b><br>
    • AI & LLM Companies<br>
    • Consumer Technology<br>
    • SaaS Platforms<br>
    • Semiconductor Companies<br>
    • Electric Vehicle Companies<br>
    • Social Media Platforms
    </p>

    </div>
    """, unsafe_allow_html=True)
_, center, _ = st.columns([1, 4, 1])
with center:
    company_input = st.text_input("Company",
                                  value=st.session_state.company_name,
                                  placeholder="Search a company or product — e.g. ChatGPT, Claude, iPhone",
                                  label_visibility="collapsed")
    analyze = st.button("Analyze Company", use_container_width=True)

if analyze and company_input:
    cached_base, is_cached = check_cached_company(company_input)
    if is_cached:
        st.session_state.update(analyzed=True, company_name=company_input,
                                analysis_success=True, from_cache=True)
        st.rerun()
    else:
        bar  = st.progress(0)
        slot = st.empty()
        slot.info(
        "Collecting news articles, YouTube videos, comments and generating reputation insights...")
        bar.progress(15)
        result = subprocess.run(["python","src/live_analysis/company_reputation.py"],
                                input=f"{company_input}\nn\n", text=True, capture_output=True)
        bar.progress(80); slot.empty()
        if result.returncode == 0:
            bar.progress(100)
            st.session_state.update(analyzed=True, company_name=company_input,
                                    analysis_success=True, from_cache=False)
            st.rerun()
        else:
            bar.empty()
            st.error("Analysis failed.")
            st.code(result.stderr)

if st.session_state.get("analysis_success"):
    cn = st.session_state.company_name
    if st.session_state.get("from_cache"):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;padding:12px 18px;'
            f'background:rgba(91,82,200,0.08);border:1px solid rgba(91,82,200,0.25);'
            f'border-radius:10px;font-size:13px;color:#9B8FEE;margin-bottom:8px;">'
            f'<span>⚡</span><span>Loaded <strong style="color:#E8EEFF;">{cn}</strong>'
            f' from cache — instant results.</span></div>', unsafe_allow_html=True)
    else:
        st.success(f"Analysis complete for **{cn}**")
    st.session_state.analysis_success = False


# ── Dashboard ─────────────────────────────────────────────────
if st.session_state.analyzed and st.session_state.company_name:
    company = st.session_state.company_name
    seed    = _seed_from(company)

    base, is_cached = check_cached_company(company)
    
    if base is not None:
        summary, analysis, issues, advisory = load_report_data(str(base))
        positive  = int(summary.loc[0,"positive"])
        neutral   = int(summary.loc[0,"neutral"])
        negative  = int(summary.loc[0,"negative"])
        score     = int(summary.loc[0,"reputation_score"])
        grade     = str(summary.loc[0,"grade"])
        risk      = str(summary.loc[0,"risk_level"])
        top_topic = str(summary.loc[0,"top_topic"])
        top_issue = issues.sort_values(by="count", ascending=False).iloc[0]["issue"]
        if "sentiment" not in analysis.columns:
            analysis["sentiment"] = ""
        if "text" not in analysis.columns:
            analysis["text"] = ""

        # ── Crisis radar: use real advisory.json if available ──
        if advisory:
            velocity = advisory["velocity"]
            alerts   = advisory["alerts"]
        else:
            # Derive from actual data
            total_m   = max(1, positive + neutral + negative)
            neg_ratio = negative / total_m
            velocity  = "High" if neg_ratio >= 0.55 else "Medium" if neg_ratio >= 0.30 else "Low"
            if risk.upper() == "HIGH":
                alerts = [
                    {"level":"critical","text":f"<strong style='color:#E8EEFF;'>Critical:</strong> {top_issue} is the dominant negative theme across {negative} mentions"},
                    {"level":"warning", "text":f"Negative ratio {neg_ratio:.0%} — monitor closely across news and YouTube"},
                ]
            elif risk.upper() == "MEDIUM":
                alerts = [
                    {"level":"warning","text":f"<strong style='color:#E8EEFF;'>Watch:</strong> {top_issue} elevated in {negative} negative mentions"},
                    {"level":"info",   "text":f"Positive sentiment holding at {positive} mentions"},
                ]
            else:
                alerts = [
                    {"level":"info","text":f"Velocity within normal range — {negative} negative out of {positive+neutral+negative} total"},
                    {"level":"info","text":f"Top discussed topic: {top_topic}"},
                ]
    else:
        import random; rng = random.Random(seed)
        score     = rng.randint(48,82)
        grade     = "Good" if score>=70 else "Fair" if score>=50 else "Poor"
        risk      = "Low"  if score>=70 else "Medium" if score>=50 else "High"
        top_topic = "Innovation"; top_issue = "Supply Chain"
        positive  = int(score*1.4); neutral = int(score*.9); negative = max(10,100-score)
        issues    = pd.DataFrame({"issue":["Supply Chain","Data Privacy","Leadership","Sustainability","Customer Service"],"count":[38,27,22,15,10]})
        analysis  = pd.DataFrame({"sentiment":[],"text":[]})
        is_cached = False
        velocity  = "Low"
        alerts    = [{"level":"info","text":"No live data — showing illustrative data"}]

    total        = max(1, positive+neutral+negative)
    s_scores     = make_stakeholder_scores(score, seed)
    velocity_df  = make_velocity_history(score, seed)
    velocity_df  = detect_anomalies(velocity_df, col="mentions")
    anomaly_events = anomaly_summary(velocity_df)
    timeline_df, timeline_events = build_timeline(company, score, seed)
    peers        = get_competitor_data(company)
    if peers:
        peers[0]["score"] = score
        peers[0]["grade"] = grade
        peers[0]["risk"]  = risk
    peers[0]["dims"] = {
    "Brand": score,
    "Innovation": min(score + 10, 100),
    "Leadership": max(score - 5, 0),
    "ESG": max(score - 10, 0),
    "Customer": score
    }

    r_bg  = ("rgba(226,80,74,.14)" if risk.upper()=="HIGH" else
             "rgba(240,160,48,.14)" if risk.upper()=="MEDIUM" else "rgba(29,173,133,.14)")
    r_col = "#F08080" if risk.upper()=="HIGH" else "#EFBF27" if risk.upper()=="MEDIUM" else "#4EC9A0"
    gu    = grade.upper()
    g_bg  = ("rgba(226,80,74,.14)" if any(w in gu for w in ["CRITICAL","POOR","F","D"])
             else "rgba(240,160,48,.14)" if any(w in gu for w in ["BELOW","FAIR","C","WEAK","MIXED"])
             else "rgba(29,173,133,.14)" if any(w in gu for w in ["GOOD","EXCELLENT","STRONG","A","B"])
             else "rgba(91,82,200,.18)")
    g_col = ("#F08080" if any(w in gu for w in ["CRITICAL","POOR","F","D"])
             else "#EFBF27" if any(w in gu for w in ["BELOW","FAIR","C","WEAK","MIXED"])
             else "#4EC9A0" if any(w in gu for w in ["GOOD","EXCELLENT","STRONG","A","B"])
             else "#9B8FEE")
    vel_col = "#E2504A" if risk.upper()=="HIGH" else "#F0A030" if risk.upper()=="MEDIUM" else "#1DAD85"

    # ── Header ────────────────────────────────────────────────
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    h_left, h_right = st.columns([6,1])
    with h_left:
        components.html(score_ring_html(score, company.title(), grade, g_bg, g_col,
                                        risk, r_bg, r_col, top_topic), height=148, scrolling=False)
    with h_right:
        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
        if st.button("↩ New search"):
            st.session_state.update(analyzed=False, company_name="", from_cache=False)

            st.rerun()

    badge_style = ("background:rgba(91,82,200,0.1);border:1px solid rgba(91,82,200,0.22);color:#9B8FEE;"
                   if is_cached else
                   "background:rgba(29,173,133,0.08);border:1px solid rgba(29,173,133,0.2);color:#4EC9A0;")
    badge_text  = "⚡ Cached report" if is_cached else "🔄 Live analysis"
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;'
        f'{badge_style}border-radius:20px;font-size:11px;font-weight:600;letter-spacing:.04em;margin-top:6px;">'
        f'{badge_text}</div>', unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    lbl("Key metrics")
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Rep. score", score)
    k2.metric("Grade", grade)
    k3.metric("Risk level", risk)
    k4.metric("Top issue", top_issue[:18]+("…" if len(top_issue)>18 else ""))
    with k5:
        st.markdown(f"""
    <div style="
    border:2px solid #22C55E;
    border-radius:16px;
    background:rgba(34,197,94,.08);
    padding:18px;
    height:118px;
    ">
    <div style="
    color:#6B7280;
    font-size:12px;
    text-transform:uppercase;
    letter-spacing:.08em;
    ">
    TOTAL MENTIONS
    </div>

    <div style="
    color:#22C55E;
    font-size:42px;
    font-weight:700;
    margin-top:10px;
    ">
    {total:,}
    </div>

    <div style="
    color:#6B7280;
    font-size:12px;
    margin-top:6px;
    ">
    Public discussions analyzed
    </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────
    tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
        "📊  Overview","🚨  Crisis radar","📈  Timeline",
        "📡 Data Sources","⚖️  Competitors","📋  CEO memo",
    ])

    # ════════════ TAB 1 — OVERVIEW ════════════
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns(2, gap="large")
        with left:
            components.html(stakeholder_html(s_scores), height=258, scrolling=False)
        with right:
            a_height = 310 if risk.upper()=="HIGH" else 262
            components.html(crisis_radar_html(velocity, risk, alerts), height=a_height, scrolling=False)

        st.markdown("<hr>", unsafe_allow_html=True)
        lbl("Issue & sentiment breakdown")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.plotly_chart(styled_bar(issues.sort_values(by="count"), x="count", y="issue",
                                       orientation="h", title="Issue distribution"),
                            use_container_width=True, key="overview_issue_bar")
        with c2:
            st.plotly_chart(donut_chart(positive, neutral, negative),
                            use_container_width=True, key="overview_donut")

        hist_path = Path("data/history/reputation_history.csv")
        if hist_path.exists():
            h_df = pd.read_csv(hist_path)
            if len(h_df) > 1:
                st.markdown("<hr>", unsafe_allow_html=True)
                lbl("Reputation trend")
                st.plotly_chart(styled_line(h_df, x="date", y="reputation_score",
                                            color="#5B52C8", title="Score over time"),
                                use_container_width=True, key="overview_trend_line")

        has_mentions = len(analysis) > 0 and "sentiment" in analysis.columns
        if has_mentions:
            st.markdown("<hr>", unsafe_allow_html=True)
            lbl("Mention detail")

            p_count = (
                analysis["sentiment"]
                .astype(str)
                .str.lower()
                .eq("positive")
                .sum()
            )

            n_count = (
                analysis["sentiment"]
                .astype(str)
                .str.lower()
                .eq("negative")
                .sum()
            )

            neu_count = (
                analysis["sentiment"]
                .astype(str)
                .str.lower()
                .eq("neutral")
                .sum()
            )

            c1, c2, c3 = st.columns(3)

            c1.metric("🟢 Positive", p_count)
            c2.metric("🔴 Negative", n_count)
            c3.metric("⚪ Neutral", neu_count)

            st.markdown("<br>", unsafe_allow_html=True)

            pt, nt, neu = st.tabs([
                f"🟢 Positive ({p_count})",
                f"🔴 Negative ({n_count})",
                f"⚪ Neutral ({neu_count})"
            ])

            with pt:

                pos_df = analysis[
                    analysis["sentiment"]
                    .astype(str)
                    .str.lower()
                    == "positive"
                ]

                if len(pos_df):

                    for txt in pos_df["text"].dropna().head(10):

                        st.markdown(
                            f'<div class="mention-pill" '
                            f'style="border-left:2px solid #1DAD85;'
                            f'background:rgba(29,173,133,0.06);">'
                            f'{txt}</div>',
                            unsafe_allow_html=True
                        )

                else:
                    st.info("No positive mentions found.")

            with nt:

                neg_df = analysis[
                    analysis["sentiment"]
                    .astype(str)
                    .str.lower()
                    == "negative"
                ]

                if len(neg_df):

                    for txt in neg_df["text"].dropna().head(10):

                        st.markdown(
                            f'<div class="mention-pill" '
                            f'style="border-left:2px solid #E2504A;'
                            f'background:rgba(226,80,74,0.06);">'
                            f'{txt}</div>',
                            unsafe_allow_html=True
                        )

                else:
                    st.info("No negative mentions found.")

            with neu:

                neu_df = analysis[
                    analysis["sentiment"]
                    .astype(str)
                    .str.lower()
                    == "neutral"
                ]

                if len(neu_df):

                    for txt in neu_df["text"].dropna().head(10):

                        st.markdown(
                            f'<div class="mention-pill" '
                            f'style="border-left:2px solid #64748B;'
                            f'background:rgba(100,116,139,0.08);">'
                            f'{txt}</div>',
                            unsafe_allow_html=True
                        )

                else:
                    st.info("No neutral mentions found.")
    # ════════════ TAB 2 — CRISIS RADAR ════════════
    # Purpose: RIGHT NOW threat assessment — velocity, severity, live alerts from real data
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)

        # Explain the tab clearly
        st.markdown(
            '<div style="background:rgba(91,82,200,0.07);border:1px solid rgba(91,82,200,0.18);'
            'border-radius:12px;padding:14px 18px;font-size:13px;color:#64748B;margin-bottom:20px;line-height:1.7;">'
            '<strong style="color:#E8EEFF;">🚨 Crisis Radar</strong> monitors the <em>current severity</em> of '
            'public sentiment — how bad is it <em>right now</em>, what are people actually saying, '
            'and does it require escalation? Unlike the Anomalies tab (which detects statistical outliers '
            'in volume over time), Crisis Radar focuses on <strong style="color:#E8EEFF;">content, '
            'velocity and risk classification</strong> from today\'s data.</div>',
            unsafe_allow_html=True)

        cr_l, cr_r = st.columns(2, gap="large")
        with cr_l:
            a_h = 340 if risk.upper()=="HIGH" else 290
            components.html(crisis_radar_html(velocity, risk, alerts), height=a_h, scrolling=False)
        with cr_r:
            lbl("Source breakdown")
            if base is not None and "source" in analysis.columns:
                src_df = (analysis.groupby(["source","sentiment"])
                          .size().reset_index(name="count"))
                fig_src = px.bar(src_df, x="source", y="count", color="sentiment",
                                 color_discrete_map={"positive":"#1DAD85","neutral":"#475569","negative":"#E2504A"},
                                 barmode="stack", title="Mentions by source & sentiment")
                fig_src.update_layout(**CHART_LAYOUT, legend=_LEGEND, height=280)
                st.plotly_chart(fig_src, use_container_width=True, key="crisis_source_bar")
            else:
                st.plotly_chart(donut_chart(positive, neutral, negative),
                                use_container_width=True, key="crisis_donut")

        st.markdown("<hr>", unsafe_allow_html=True)
        lbl("Mention velocity — 30 days")
        st.plotly_chart(anomaly_chart(velocity_df, col="mentions", line_color=vel_col),
                        use_container_width=True, key="crisis_velocity_chart")

        st.markdown("<hr>", unsafe_allow_html=True)
        lbl("Issue severity classification")
        issues_s = issues.sort_values(by="count", ascending=False).head(8).copy()
        q66, q33 = issues_s["count"].quantile(0.66), issues_s["count"].quantile(0.33)
        issues_s["severity"]  = issues_s["count"].apply(lambda x: "🔴 High" if x>=q66 else "🟡 Medium" if x>=q33 else "🟢 Low")
        issues_s["risk_type"] = issues_s["issue"].apply(
            lambda i: "Reputational" if any(w in i.lower() for w in ["fraud","scandal","ceo","leak","lawsuit","leadership"])
                      else "Operational" if any(w in i.lower() for w in ["product","service","outage","recall","quality"])
                      else "Financial"   if any(w in i.lower() for w in ["stock","revenue","loss","profit","volatility"])
                      else "AI/Tech"     if any(w in i.lower() for w in ["ai","safety","bias","privacy","data","regulation"])
                      else "General")
        st.dataframe(
            issues_s[["issue","count","severity","risk_type"]].rename(
                columns={"issue":"Issue","count":"Mentions","severity":"Severity","risk_type":"Risk type"}),
            use_container_width=True, hide_index=True)

    # ════════════ TAB 3 — TIMELINE ════════════
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        lbl("Reputation score — 90-day history")
        st.markdown("""
        <div style="
        background:#0C1120;
        border:1px solid #182030;
        border-radius:12px;
        padding:16px 20px;
        margin-bottom:18px;
        color:#C9D4F5;
        line-height:1.7;
        font-size:13px;
        ">

        <b style="color:#E8EEFF;">📈 Reputation Timeline</b><br>

        This chart visualizes the company's <b>reputation score over time</b> based on
        public discussions collected from news articles, YouTube videos, and YouTube
        comments. It helps identify improvements, declines, and long-term reputation
        trends.

        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(timeline_chart(timeline_df, timeline_events, company),
                        use_container_width=True, key="timeline_main_chart")
        st.markdown("<hr>", unsafe_allow_html=True)
        ev_col, info_col = st.columns(2, gap="large")
        with ev_col:
            lbl("Event log")
            ev_html = timeline_events_html(timeline_events)
            if ev_html:
                components.html(ev_html, height=min(100 + len(timeline_events)*80, 500), scrolling=False)
            else:
                st.info("No significant events detected.")
        with info_col:
            lbl("Score statistics")
            if len(timeline_df) > 1:
                t = timeline_df["reputation_score"]
                s1,s2,s3 = st.columns(3)
                s1.metric("Peak",  int(t.max()))
                s2.metric("Low",   int(t.min()))
                s3.metric("Avg",   int(t.mean()))
                st.markdown("<br>", unsafe_allow_html=True)
                s4,s5 = st.columns(2)
                s4.metric("Best day",  timeline_df.loc[t.idxmax(),"date"])
                s5.metric("Worst day", timeline_df.loc[t.idxmin(),"date"])
                st.markdown("<br>", unsafe_allow_html=True)
                td = t.iloc[45:].mean() - t.iloc[:45].mean()
                tl = "Improving" if td>2 else "Declining" if td<-2 else "Stable"
                tc = "#1DAD85" if td>2 else "#E2504A" if td<-2 else "#F0A030"
                st.markdown(
                    f'<div style="background:#0C1120;border:1px solid #182030;border-radius:12px;padding:16px 20px;">'
                    f'<div style="font-size:11px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;">30-day trend</div>'
                    f'<div style="font-size:22px;font-weight:700;color:{tc};">{tl}</div>'
                    f'<div style="font-size:12px;color:#3A4F6E;margin-top:4px;">{"+" if td>=0 else ""}{td:.1f} pts vs prior 30 days</div>'
                    f'</div>', unsafe_allow_html=True)

    # ════════════ TAB 4 — DATA SOURCES ════════════
    with tab4:

        st.markdown("<hr>", unsafe_allow_html=True)

        lbl("Data collection summary")

        news_count = (
            analysis["source"]
            .astype(str)
            .str.contains("news", case=False, na=False)
            .sum()
        )

        video_count = (
            analysis["source"]
            .astype(str)
            .str.contains("youtube_video", case=False, na=False)
            .sum()
        )

        comment_count = (
            analysis["source"]
            .astype(str)
            .str.contains("youtube_comment", case=False, na=False)
            .sum()
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("📰 News", news_count)
        c2.metric("🎥 Videos", video_count)
        c3.metric("💬 Comments", comment_count)
        c4.metric("📊 Total", len(analysis))

        st.markdown("<br>", unsafe_allow_html=True)

        lbl("Project scope")

        st.info(
            f"""
            Company: {company.title()}

            Data Sources:
            • News Articles
            • YouTube Videos
            • YouTube Comments

            Collection Window:
            • Latest available public data

            Analysis Includes:
            • Sentiment Analysis
            • Topic Detection
            • Issue Extraction
            • Reputation Scoring
            • Crisis Detection
            • Competitor Benchmarking
            """
        )

        lbl("Reputation score methodology")

        st.markdown(
            """
            - Positive sentiment increases score
            - Negative sentiment decreases score
            - High-risk issues reduce score
            - Issue frequency impacts reputation grade
            - Overall score determines risk level and executive recommendations
            """
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if "source" in analysis.columns:

            src_counts = (
                analysis["source"]
                .value_counts()
                .reset_index()
            )

            src_counts.columns = ["Source", "Count"]

            st.dataframe(
                src_counts,
                use_container_width=True,
                hide_index=True
            )
    # ════════════ TAB 5 — COMPETITORS ════════════
    with tab5:
        st.markdown("<br>", unsafe_allow_html=True)

        # Score comparison cards
        lbl(f"{company.title()} vs peers — reputation scores")
        simple_peers = [(p["name"], p["score"], p["grade"], p["risk"]) for p in peers]
        components.html(competitor_cards_html(peers), height=240, scrolling=False)

        st.markdown("<br>", unsafe_allow_html=True)


        # Radar chart
        if len(peers) >= 2:
            lbl("Dimension radar — where they win and lose")
            dims_order = ["Brand","Innovation","Leadership","ESG","Customer"]
            fig_r = go.Figure()
            colors_r = ["#5B52C8","#1DAD85","#F0A030","#E2504A","#9B8FEE"]
            fills_r  = ["rgba(91,82,200,0.12)","rgba(29,173,133,0.08)",
                        "rgba(240,160,48,0.08)","rgba(226,80,74,0.08)","rgba(155,143,238,0.08)"]
            for i, p in enumerate(peers[:4]):
                vals = [p["dims"].get(d, p["score"]) for d in dims_order]
                fig_r.add_trace(go.Scatterpolar(
                    r=vals+[vals[0]], theta=dims_order+[dims_order[0]],
                    fill="toself", name=p["name"],
                    line=dict(color=colors_r[i % len(colors_r)], width=2),
                    fillcolor=fills_r[i % len(fills_r)],
                ))
            fig_r.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#64748B", size=12), height=400,
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(visible=True, range=[0,100], gridcolor="#131E34",
                                           tickfont=dict(color="#3A4F6E"), linecolor="#131E34"),
                           angularaxis=dict(gridcolor="#131E34", linecolor="#131E34",
                                            tickfont=dict(color="#94A3B8"))),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")),
                margin=dict(l=40,r=40,t=30,b=30))
            st.plotly_chart(fig_r, use_container_width=True, key="comp_radar_chart")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── NEW: Why they score the way they do ──
        lbl("Competitive intelligence — why they score the way they do")
        detail_height = len(peers) * 320
        components.html(competitor_detail_html(peers), height=detail_height, scrolling=True)

    # ════════════ TAB 6 — CEO MEMO ════════════
    with tab6:
        st.markdown("<br>", unsafe_allow_html=True)
        components.html(memo_html(score, grade, risk, top_issue, company.title()), height=420, scrolling=False)
        st.markdown("<br>", unsafe_allow_html=True)
        lbl("Export")
        pdf_col, _ = st.columns([1,3])
        with pdf_col:
            if st.button("⬇  Export memo as PDF"):
                pdf_bytes = generate_pdf(company, score, grade, risk, top_issue)
                if pdf_bytes:
                    b64   = base64.b64encode(pdf_bytes).decode()
                    fname = f"{company.lower().replace(' ','_')}_memo_{datetime.now().strftime('%Y%m%d')}.pdf"
                    st.markdown(f'<div class="dl-link"><a href="data:application/pdf;base64,{b64}" '
                                f'download="{fname}">📄 Download PDF memo</a></div>', unsafe_allow_html=True)
                else:
                    st.warning("Install `reportlab`: `pip install reportlab`")
        st.markdown("<br>", unsafe_allow_html=True)
        lbl("Plain text")
        st.code(f"""CEO Briefing — {company.title()}
Date: {datetime.now().strftime('%B %d, %Y')}

Reputation Score : {score} | Grade: {grade} | Risk: {risk}
Primary Issue    : {top_issue}
Crisis Velocity  : {velocity}

Executive Summary:
Negative discussion is concentrated around {top_issue}.
Public perception indicates a {risk.lower()} risk environment.
Stakeholder trust is strongest with customers and requires attention at the employee level.

Recommended Actions:
1. Increase executive transparency on {top_issue.lower()}
2. Accelerate internal communications to address employee sentiment
3. Monitor media velocity daily until risk normalises
4. Brief investor relations before next earnings call

Generated by SocialMind AI""", language=None)