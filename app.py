import streamlit as st
import streamlit.components.v1 as components
import subprocess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io, base64, hashlib
from datetime import datetime, timedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SocialMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global styles ─────────────────────────────────────────────────────────────
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


# ── Chart constants ───────────────────────────────────────────────────────────
# FIX 1: CHART_LAYOUT must NOT include 'legend' — charts that need custom
# legend config pass it separately to avoid "multiple values" TypeError.
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#64748B", size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    xaxis=dict(gridcolor="#131E34", linecolor="#131E34", tickfont=dict(color="#64748B")),
    yaxis=dict(gridcolor="#131E34", linecolor="#131E34", tickfont=dict(color="#64748B")),
)
# Separate default legend config — merge manually where needed
_LEGEND = dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B"))

PALETTE = ["#5B52C8","#1DAD85","#F0A030","#E2504A","#9B8FEE","#4EC9A0","#60A5FA"]


# ── iframe head (fonts via <link>, not @import) ───────────────────────────────
def _head():
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
        '&family=DM+Mono:wght@500&display=swap" rel="stylesheet">'
        '<style>*{font-family:Inter,sans-serif!important;box-sizing:border-box;margin:0;padding:0;}'
        'body{background:transparent;overflow:hidden;}</style>'
    )


# ── Chart helpers ─────────────────────────────────────────────────────────────
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


# ── Section label ─────────────────────────────────────────────────────────────
def lbl(text):
    st.markdown(
        f'<div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;'
        f'text-transform:uppercase;margin-bottom:12px;margin-top:6px;">{text}</div>',
        unsafe_allow_html=True,
    )


# ── HTML component builders ───────────────────────────────────────────────────
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

def competitor_cards_html(companies_data):
    cards = ""
    for i, (name, score, grade, risk) in enumerate(companies_data):
        ring_col = "#1DAD85" if score>=70 else "#F0A030" if score>=45 else "#E2504A"
        pct  = max(0, min(score/100, 1))
        circ = 2*3.14159*22
        dash, gap = pct*circ, (1-pct)*circ
        border = "#5B52C8" if i==0 else "#182030"
        badge  = "<div style='font-size:9px;font-weight:700;letter-spacing:.1em;color:#5B52C8;text-transform:uppercase;margin-bottom:6px;'>PRIMARY</div>" if i==0 else ""
        cards += f"""
        <div style="flex:1;min-width:140px;background:#0C1120;border:1px solid {border};
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
              <div style="font-size:14px;font-weight:700;color:#E8EEFF;">{name}</div>
              <div style="font-size:11px;color:#2E3D58;margin-top:2px;">{grade} · {risk} risk</div>
            </div>
          </div>
          <div style="height:3px;background:#182030;border-radius:2px;overflow:hidden;">
            <div style="height:100%;width:{score}%;background:{ring_col};border-radius:2px;"></div>
          </div>
        </div>"""
    return f"""{_head()}
<div style="display:flex;gap:12px;flex-wrap:wrap;">{cards}</div>"""

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
            <strong style="color:{col};">{arrow} {label} — {e["date"]}</strong><br>
            {e["value"]:,} mentions &nbsp;·&nbsp; {e["pct_dev"]}% above normal &nbsp;·&nbsp;
            z-score <span style="font-family:DM Mono,monospace;">{e["z"]}</span>
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
            <div style="font-size:11px;color:#3A4F6E;margin-bottom:3px;">{e["date"]}</div>
            <div style="font-size:13px;color:#E8EEFF;font-weight:600;">{e["label"]}</div>
            <div style="font-size:12px;color:{dlt_col};margin-top:2px;">
              {arrow} {abs(e["delta"])} pts &nbsp;·&nbsp;
              Score: <span style="font-family:DM Mono,monospace;">{e["score"]}</span>
            </div>
          </div>
        </div>"""
    return f"""{_head()}
<div style="background:#0C1120;border:1px solid #182030;border-radius:16px;padding:20px 24px;">
  <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;
       text-transform:uppercase;margin-bottom:14px;">📅 Event log</div>
  {items}
</div>"""


# ── Synthetic / derived data helpers ─────────────────────────────────────────
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

    # Inject 1-2 guaranteed anomalies so the feature has something to show.
    # Real news-driven mention data naturally has spikes; smooth synthetic
    # noise often doesn't cross the z-score threshold on its own.
    spike_day = rng.randint(18, 27)
    vals[spike_day] = int(base * rng.uniform(2.8, 4.0))  # clear spike

    if risk_allows_drop := rng.random() < 0.6:
        drop_day = rng.randint(5, 14)
        if drop_day != spike_day:
            vals[drop_day] = max(2, int(base * rng.uniform(0.1, 0.3)))  # clear drop

    return pd.DataFrame({"date": dates, "mentions": vals})

def derive_crisis_data(risk, top_issue):
    if risk.upper() == "HIGH":
        return "High", [
            {"level":"critical","text":f"<strong style='color:#E8EEFF;'>Critical:</strong> {top_issue} mentions spiked 3× baseline in last 6 hours"},
            {"level":"warning", "text":"Negative conversation volume above threshold — media pickup detected"},
            {"level":"warning", "text":"Investor-sentiment keywords trending downward on financial forums"},
        ]
    elif risk.upper() == "MEDIUM":
        return "Medium", [
            {"level":"warning","text":f"<strong style='color:#E8EEFF;'>Watch:</strong> Elevated discussion around {top_issue}"},
            {"level":"info",   "text":"Innovation and product sentiment holding steady"},
        ]
    else:
        return "Low", [
            {"level":"info","text":"Mention velocity within normal range — no immediate action required"},
            {"level":"info","text":"Innovation sentiment remains strong across all monitored channels"},
        ]


# ── Anomaly detection ─────────────────────────────────────────────────────────
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

def anomaly_chart(df, col="mentions", line_color="#5B52C8"):
    # FIX 1: don't pass legend inside update_layout alongside **CHART_LAYOUT
    # because CHART_LAYOUT no longer contains 'legend' this is now safe.
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


# ── Historical timeline ───────────────────────────────────────────────────────
def build_timeline(company_name, current_score, seed):
    hist_path = Path("data/history/reputation_history.csv")
    if hist_path.exists():
        df = pd.read_csv(hist_path)
        if len(df) >= 7 and "reputation_score" in df.columns:
            df = df.tail(90).copy()
            if "date" not in df.columns:
                df["date"] = pd.date_range(end=datetime.now(), periods=len(df),
                                           freq="D").strftime("%b %d")
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


# ── Competitor data ───────────────────────────────────────────────────────────
COMPETITOR_PAIRS = {
    "tesla":     [("Tesla",72,"Good","Low"),("Rivian",58,"Fair","Medium"),("Lucid",49,"Fair","Medium"),("Ford EV",54,"Fair","Medium")],
    "rivian":    [("Rivian",58,"Fair","Medium"),("Tesla",72,"Good","Low"),("Lucid",49,"Fair","Medium")],
    "openai":    [("OpenAI",68,"Good","Medium"),("Anthropic",74,"Good","Low"),("Google DeepMind",65,"Good","Medium"),("Mistral",60,"Fair","Medium")],
    "anthropic": [("Anthropic",74,"Good","Low"),("OpenAI",68,"Good","Medium"),("Google DeepMind",65,"Good","Medium")],
    "nvidia":    [("Nvidia",80,"Excellent","Low"),("AMD",67,"Good","Low"),("Intel",54,"Fair","Medium"),("Qualcomm",66,"Good","Low")],
    "amd":       [("AMD",67,"Good","Low"),("Nvidia",80,"Excellent","Low"),("Intel",54,"Fair","Medium")],
    "apple":     [("Apple",85,"Excellent","Low"),("Samsung",72,"Good","Low"),("Google",78,"Good","Low"),("Microsoft",82,"Excellent","Low")],
    "microsoft": [("Microsoft",82,"Excellent","Low"),("Google",78,"Good","Low"),("Apple",85,"Excellent","Low"),("Amazon",69,"Good","Low")],
    "google":    [("Google",78,"Good","Low"),("Microsoft",82,"Excellent","Low"),("Apple",85,"Excellent","Low"),("Meta",55,"Fair","Medium")],
    "meta":      [("Meta",55,"Fair","Medium"),("Snap",50,"Fair","High"),("TikTok",52,"Fair","High"),("LinkedIn",68,"Good","Low")],
    "amazon":    [("Amazon",69,"Good","Low"),("Walmart",62,"Good","Medium"),("Microsoft",82,"Excellent","Low"),("Shopify",65,"Good","Low")],
    "samsung":   [("Samsung",72,"Good","Low"),("Apple",85,"Excellent","Low"),("Xiaomi",60,"Fair","Medium"),("Sony",68,"Good","Low")],
}

def get_competitor_data(company_name):
    key = company_name.lower()
    for k, v in COMPETITOR_PAIRS.items():
        if k in key or key in k:
            return v
    import random; rng = random.Random(_seed_from(company_name) + 2)
    base = rng.randint(50,85)
    return [(company_name, base, "Good" if base>=70 else "Fair", "Low" if base>=70 else "Medium")]


# ── PDF export ────────────────────────────────────────────────────────────────
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
        def ps(base, **kw):
            return ParagraphStyle(base+"_c", parent=styles[base], **kw)
        accent = colors.HexColor("#5B52C8")
        dark   = colors.HexColor("#1E293B")
        story  = [
            Paragraph("🧠 SocialMind AI", ps("Normal", fontSize=9, textColor=accent, spaceAfter=4)),
            Paragraph(f"CEO Briefing — {company}", ps("Title", fontSize=24, textColor=dark, spaceAfter=4)),
            Paragraph(datetime.now().strftime("%B %d, %Y"),
                      ps("Normal", fontSize=10, textColor=colors.HexColor("#64748B"), spaceAfter=16)),
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
            f"Public perception indicates a <b>{risk.lower()} risk</b> environment. "
            "Stakeholder trust is strongest with customers and requires attention at the employee level.",
            ps("Normal", fontSize=11, leading=18, spaceAfter=14)))
        story.append(Paragraph("Recommended Actions", ps("Heading2", textColor=dark, spaceAfter=8)))
        for a in [f"Increase executive transparency on <b>{top_issue.lower()}</b>",
                  "Accelerate internal communications cadence",
                  "Monitor media velocity daily and trigger escalation if risk worsens",
                  "Brief investor relations before next earnings call"]:
            story.append(Paragraph(f"• {a}", ps("Normal", fontSize=11, leading=17, leftIndent=12, spaceAfter=6)))
        story += [Spacer(1,20),
                  HRFlowable(width="100%", thickness=.5, color=colors.HexColor("#E2E8F0")),
                  Paragraph("Generated by SocialMind AI · Confidential",
                             ps("Normal", fontSize=8, textColor=colors.HexColor("#94A3B8"), spaceBefore=8))]
        doc.build(story)
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None


# ── Data loading ──────────────────────────────────────────────────────────────
def _find_csv(folder, *candidates):
    for name in candidates:
        p = folder / name
        if p.exists():
            return p
    return None

def check_cached_company(company_name):
    # Check saved companies first
    companies_root = Path("data/companies")
    if companies_root.exists():
        for folder in companies_root.iterdir():
            if folder.is_dir() and folder.name.lower() == company_name.strip().lower():
                if (_find_csv(folder, "reputation_summary.csv") and
                    _find_csv(folder, "company_dataset.csv", "reputation_analysis.csv") and
                    _find_csv(folder, "issue_summary.csv")):
                    return folder, True
    # FIX 3: was incorrectly reusing loop variable 'folder' — now uses explicit 'live'
    live = Path("data/live")
    if (_find_csv(live, "reputation_summary.csv") and
        _find_csv(live, "reputation_analysis.csv", "company_dataset.csv") and
        _find_csv(live, "issue_summary.csv")):
        return live, False
    return None, False

@st.cache_data(ttl=600, show_spinner=False)
def load_report_data(base_path_str):
    base     = Path(base_path_str)
    summary  = pd.read_csv(_find_csv(base, "reputation_summary.csv"))
    # FIX 2a: try both filenames for analysis CSV
    analysis = pd.read_csv(_find_csv(base, "reputation_analysis.csv", "company_dataset.csv"))
    issues   = pd.read_csv(_find_csv(base, "issue_summary.csv"))
    # FIX 2b: normalise column names so downstream code always sees 'sentiment' and 'text'
    analysis.columns = [c.lower().strip() for c in analysis.columns]
    if "content" in analysis.columns and "text" not in analysis.columns:
        analysis = analysis.rename(columns={"content": "text"})
    if "label" in analysis.columns and "sentiment" not in analysis.columns:
        analysis = analysis.rename(columns={"label": "sentiment"})
    return summary, analysis, issues


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("analyzed",False),("company_name",""),("analysis_success",False),("from_cache",False)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ── Landing ───────────────────────────────────────────────────────────────────
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
        and brief your leadership — all from a single search.
      </div>
    </div>
    """, unsafe_allow_html=True)

_, center, _ = st.columns([1, 4, 1])
with center:
    company_input = st.text_input("Company",
                                  value=st.session_state.company_name,
                                  placeholder="Search a company — e.g. Apple, Tesla, OpenAI",
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
        slot.info("Fetching news articles...")
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


# ── Dashboard ─────────────────────────────────────────────────────────────────
if st.session_state.analyzed and st.session_state.company_name:
    company = st.session_state.company_name
    seed    = _seed_from(company)

    base, is_cached = check_cached_company(company)
    load_report_data.clear()  # always reload fresh — avoids stale cache on column changes

    if base is not None:
        summary, analysis, issues = load_report_data(str(base))
        positive  = int(summary.loc[0,"positive"])
        neutral   = int(summary.loc[0,"neutral"])
        negative  = int(summary.loc[0,"negative"])
        score     = int(summary.loc[0,"reputation_score"])
        grade     = str(summary.loc[0,"grade"])
        risk      = str(summary.loc[0,"risk_level"])
        top_topic = str(summary.loc[0,"top_topic"])
        top_issue = issues.sort_values(by="count", ascending=False).iloc[0]["issue"]
        # FIX 2b: if sentiment column is still missing after normalisation, create empty
        if "sentiment" not in analysis.columns:
            analysis["sentiment"] = ""
        if "text" not in analysis.columns:
            analysis["text"] = ""
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

    total            = max(1, positive+neutral+negative)
    s_scores         = make_stakeholder_scores(score, seed)
    velocity, alerts = derive_crisis_data(risk, top_issue)
    velocity_df      = make_velocity_history(score, seed)
    velocity_df      = detect_anomalies(velocity_df, col="mentions")
    anomaly_events   = anomaly_summary(velocity_df)
    timeline_df, timeline_events = build_timeline(company, score, seed)
    comp_data        = get_competitor_data(company)

    r_bg  = ("rgba(226,80,74,.14)" if risk.upper()=="HIGH" else
             "rgba(240,160,48,.14)" if risk.upper()=="MEDIUM" else "rgba(29,173,133,.14)")
    r_col = "#F08080" if risk.upper()=="HIGH" else "#EFBF27" if risk.upper()=="MEDIUM" else "#4EC9A0"
    gu    = grade.upper()
    g_bg  = ("rgba(226,80,74,.14)" if any(w in gu for w in ["CRITICAL","POOR","F","D"])
             else "rgba(240,160,48,.14)" if any(w in gu for w in ["BELOW","FAIR","C"])
             else "rgba(29,173,133,.14)" if any(w in gu for w in ["GOOD","EXCELLENT","A","B"])
             else "rgba(91,82,200,.18)")
    g_col = ("#F08080" if any(w in gu for w in ["CRITICAL","POOR","F","D"])
             else "#EFBF27" if any(w in gu for w in ["BELOW","FAIR","C"])
             else "#4EC9A0" if any(w in gu for w in ["GOOD","EXCELLENT","A","B"])
             else "#9B8FEE")
    vel_col = "#E2504A" if risk.upper()=="HIGH" else "#F0A030" if risk.upper()=="MEDIUM" else "#1DAD85"

    # ── Header ────────────────────────────────────────────────
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    h_left, h_right = st.columns([6,1])
    with h_left:
        components.html(score_ring_html(score, company, grade, g_bg, g_col,
                                        risk, r_bg, r_col, top_topic),
                        height=148, scrolling=False)
    with h_right:
        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
        if st.button("↩ New search"):
            st.session_state.update(analyzed=False, company_name="", from_cache=False)
            load_report_data.clear()
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
    k5.metric("Total mentions", f"{total:,}")
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────
    tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
        "📊  Overview","🚨  Crisis radar","📈  Timeline",
        "🔍  Anomalies","⚖️  Competitors","📋  CEO memo",
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
                            use_container_width=True)
        with c2:
            st.plotly_chart(donut_chart(positive, neutral, negative), use_container_width=True)

        hist_path = Path("data/history/reputation_history.csv")
        if hist_path.exists():
            h_df = pd.read_csv(hist_path)
            if len(h_df) > 1:
                st.markdown("<hr>", unsafe_allow_html=True)
                lbl("Reputation trend")
                st.plotly_chart(styled_line(h_df, x="date", y="reputation_score",
                                            color="#5B52C8", title="Score over time"),
                                use_container_width=True)

        # Show mentions whenever we have rows and a sentiment column
        has_mentions = len(analysis) > 0 and "sentiment" in analysis.columns
        if has_mentions:
            st.markdown("<hr>", unsafe_allow_html=True)
            lbl("Mention detail")
            pt, nt = st.tabs(["Positive mentions","Negative mentions"])
            with pt:
                pos_df = analysis[analysis["sentiment"].astype(str).str.lower()=="positive"]
                if len(pos_df):
                    for txt in pos_df["text"].head(10):
                        st.markdown(f'<div class="mention-pill" style="border-left:2px solid #1DAD85;'
                                    f'background:rgba(29,173,133,0.06);">{txt}</div>',
                                    unsafe_allow_html=True)
                else:
                    st.info("No positive mentions found.")
            with nt:
                neg_df = analysis[analysis["sentiment"].astype(str).str.lower()=="negative"]
                if len(neg_df):
                    for txt in neg_df["text"].head(10):
                        st.markdown(f'<div class="mention-pill" style="border-left:2px solid #E2504A;'
                                    f'background:rgba(226,80,74,0.06);">{txt}</div>',
                                    unsafe_allow_html=True)
                else:
                    st.info("No negative mentions found.")

    # ════════════ TAB 2 — CRISIS RADAR ════════════
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        lbl("Mention velocity — 30 days (with anomaly markers)")
        st.plotly_chart(anomaly_chart(velocity_df, col="mentions", line_color=vel_col),
                        use_container_width=True,key="anomaly_chart2")
        if anomaly_events:
            st.markdown(
                f'<div style="font-size:12px;color:#E2504A;margin-top:-6px;margin-bottom:12px;">'
                f'⚠ {len(anomaly_events)} anomal{"y" if len(anomaly_events)==1 else "ies"} detected '
                f'— see Anomalies tab for detail.</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        lbl("Risk classification · Issue severity")
        issues_s = issues.sort_values(by="count", ascending=False).head(8).copy()
        q66, q33 = issues_s["count"].quantile(0.66), issues_s["count"].quantile(0.33)
        issues_s["severity"]  = issues_s["count"].apply(lambda x: "🔴 High" if x>=q66 else "🟡 Medium" if x>=q33 else "🟢 Low")
        issues_s["risk_type"] = issues_s["issue"].apply(
            lambda i: "Reputational" if any(w in i.lower() for w in ["fraud","scandal","ceo","leak","lawsuit"])
                      else "Operational" if any(w in i.lower() for w in ["product","service","outage","recall"])
                      else "Financial"   if any(w in i.lower() for w in ["stock","revenue","loss","profit","volatility"])
                      else "General")
        st.dataframe(issues_s[["issue","count","severity","risk_type"]].rename(
            columns={"issue":"Issue","count":"Mentions","severity":"Severity","risk_type":"Risk type"}),
            use_container_width=True, hide_index=True)
        st.markdown("<br>", unsafe_allow_html=True)
        a_h = 310 if risk.upper()=="HIGH" else 262
        components.html(crisis_radar_html(velocity, risk, alerts), height=a_h, scrolling=False)

    # ════════════ TAB 3 — TIMELINE ════════════
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        lbl("Reputation score — 90-day history")
        st.plotly_chart(timeline_chart(timeline_df, timeline_events, company),
                        use_container_width=True,key="source_chart")
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

    # ════════════ TAB 4 — ANOMALIES ════════════
    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        spike_count = len([e for e in anomaly_events if e["dir"]=="spike"])
        drop_count  = len([e for e in anomaly_events if e["dir"]=="drop"])
        max_z       = max((abs(e["z"]) for e in anomaly_events), default=0.0)
        overall     = "Critical" if max_z>=4.0 else "Warning" if max_z>=2.5 else "Normal"
        a1,a2,a3,a4 = st.columns(4)
        a1.metric("Anomalies",  spike_count+drop_count)
        a2.metric("Spikes",     spike_count)
        a3.metric("Drops",      drop_count)
        a4.metric("Max z-score",f"{max_z:.1f}", delta=overall)
        st.markdown("<hr>", unsafe_allow_html=True)
        lbl("Mention volume with anomaly markers")
        st.plotly_chart(anomaly_chart(velocity_df, col="mentions", line_color=vel_col),
                        use_container_width=True,key="anomaly_chart1")
        st.markdown(
            '<div style="display:flex;gap:20px;font-size:12px;color:#3A4F6E;margin-top:-8px;margin-bottom:16px;">'
            '<span>▲ <span style="color:#E2504A;">Red</span> = spike (z≥2.0)</span>'
            '<span>▼ <span style="color:#F0A030;">Amber</span> = drop</span>'
            '<span>── Dotted = 7-day avg</span>'
            '<span>■ Band = normal range (±1.5σ)</span></div>', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        al, ar = st.columns(2, gap="large")
        with al:
            lbl("Detected anomalies")
            if anomaly_events:
                components.html(anomaly_alert_html(anomaly_events),
                                height=min(100+len(anomaly_events[:5])*78, 480), scrolling=False)
            else:
                st.success("No anomalies detected — velocity within normal range.")
        with ar:
            lbl("Z-score distribution")
            zf = go.Figure()
            zf.add_trace(go.Bar(x=velocity_df["date"], y=velocity_df["z_score"],
                                marker_color=["#E2504A" if z>=2 else "#F0A030" if z<=-2 else "#182030"
                                              for z in velocity_df["z_score"]], name="Z-score"))
            zf.add_hline(y=2.0,  line_dash="dot", line_color="#E2504A",
                         annotation_text="spike",annotation_font_color="#E2504A")
            zf.add_hline(y=-2.0, line_dash="dot", line_color="#F0A030",
                         annotation_text="drop", annotation_font_color="#F0A030")
            zf.update_layout(**CHART_LAYOUT, legend=_LEGEND, height=300, yaxis_title="z-score", showlegend=False)
            st.plotly_chart(zf, use_container_width=True,key="confidence_chart")

    # ════════════ TAB 5 — COMPETITORS ════════════
    with tab5:
        st.markdown("<br>", unsafe_allow_html=True)
        lbl(f"{company.title()} vs peers")
        components.html(competitor_cards_html(comp_data), height=240, scrolling=False)
        st.markdown("<br>", unsafe_allow_html=True)
        if len(comp_data) > 1:
            bench_df = pd.DataFrame(comp_data, columns=["Company","Score","Grade","Risk"])
            fig_b = px.bar(bench_df, x="Company", y="Score", color="Company",
                           color_discrete_sequence=PALETTE, title="Reputation score comparison", text="Score")
            fig_b.update_traces(marker_line_width=0, textposition="outside", textfont=dict(color="#64748B",size=11))
            fig_b.update_layout(**CHART_LAYOUT, legend=_LEGEND, height=320, showlegend=False)
            st.plotly_chart(fig_b, use_container_width=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            lbl("Dimension radar")
            dims  = ["Products","Leadership","Workplace","ESG","Financials"]
            s0, s1 = comp_data[0][1], comp_data[1][1]
            vals0 = [min(100,s0+15),min(100,s0-10),min(100,s0-5),min(100,s0+5),min(100,s0+8)]
            vals1 = [min(100,s1+10),min(100,s1-8), min(100,s1+2),min(100,s1+6),min(100,s1-3)]
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(r=vals0+[vals0[0]], theta=dims+[dims[0]], fill="toself",
                                             name=comp_data[0][0], line=dict(color="#5B52C8",width=2),
                                             fillcolor="rgba(91,82,200,0.12)"))
            fig_r.add_trace(go.Scatterpolar(r=vals1+[vals1[0]], theta=dims+[dims[0]], fill="toself",
                                             name=comp_data[1][0], line=dict(color="#1DAD85",width=2),
                                             fillcolor="rgba(29,173,133,0.08)"))
            fig_r.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter",color="#64748B",size=12), height=400,
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(visible=True,range=[0,100],gridcolor="#131E34",
                                           tickfont=dict(color="#3A4F6E"),linecolor="#131E34"),
                           angularaxis=dict(gridcolor="#131E34",linecolor="#131E34",
                                            tickfont=dict(color="#94A3B8"))),
                legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#94A3B8")),
                margin=dict(l=40,r=40,t=30,b=30))
            st.plotly_chart(fig_r, use_container_width=True,key="comparison_chart")

    # ════════════ TAB 6 — CEO MEMO ════════════
    with tab6:
        st.markdown("<br>", unsafe_allow_html=True)
        components.html(memo_html(score, grade, risk, top_issue, company.title()),
                        height=420, scrolling=False)
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
                                f'download="{fname}">📄 Download PDF memo</a></div>',
                                unsafe_allow_html=True)
                else:
                    st.warning("Install `reportlab`: `pip install reportlab`")
        st.markdown("<br>", unsafe_allow_html=True)
        lbl("Plain text")
        st.code(f"""CEO Briefing — {company}
Date: {datetime.now().strftime('%B %d, %Y')}

Reputation Score: {score} | Grade: {grade} | Risk: {risk}
Primary Issue: {top_issue}

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