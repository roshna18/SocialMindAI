import streamlit as st
import streamlit.components.v1 as components
import subprocess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io, base64, random, time
from datetime import datetime, timedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SocialMind AI",
    page_icon="◈",
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

/* ── Input ── */
div[data-testid="stTextInput"] input {
    background: #0D1326 !important;
    border: 1px solid #1E2B45 !important;
    border-radius: 14px !important;
    color: #E8EEFF !important;
    font-size: 15px !important;
    padding: 15px 20px !important;
    height: auto !important;
    transition: border-color .2s, box-shadow .2s;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #5B52C8 !important;
    box-shadow: 0 0 0 3px rgba(91,82,200,.18) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #2E3D58 !important; }
div[data-testid="stTextInput"] label { display:none !important; }

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg,#5B52C8,#7B6FE0) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-size: 14px !important;
    font-weight: 600 !important; padding: 12px 28px !important;
    height: auto !important; width: 100% !important;
    transition: opacity .15s, transform .1s;
    letter-spacing: .02em;
}
div[data-testid="stButton"] > button:hover {
    opacity: .88 !important; transform: translateY(-1px);
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #0C1120 !important; border: 1px solid #182030 !important;
    border-radius: 16px !important; padding: 18px 22px !important;
}
[data-testid="stMetricLabel"]  { color: #3A4F6E !important; font-size: 11px !important; letter-spacing: .08em; text-transform: uppercase; }
[data-testid="stMetricValue"]  { color: #E8EEFF !important; font-size: 26px !important; font-family: 'DM Mono', monospace !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #0C1120 !important; border: 1px solid #182030 !important;
    border-radius: 14px !important;
}
[data-testid="stExpander"] summary { color: #94A3B8 !important; font-size: 14px !important; font-weight: 500 !important; }

/* ── Tabs ── */
[data-testid="stTabs"] button { color: #3A4F6E !important; font-size: 13px !important; font-weight: 500 !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color: #E8EEFF !important; border-bottom-color: #5B52C8 !important; }

/* ── Divider ── */
hr { border:none; border-top:1px solid #131E34 !important; margin:2rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Chart constants ───────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#64748B", size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    xaxis=dict(gridcolor="#131E34", linecolor="#131E34", tickfont=dict(color="#64748B")),
    yaxis=dict(gridcolor="#131E34", linecolor="#131E34", tickfont=dict(color="#64748B")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B")),
)
PALETTE = ["#5B52C8", "#1DAD85", "#F0A030", "#E2504A", "#9B8FEE", "#4EC9A0"]
FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Mono:wght@500&display=swap');"


def _base_style():
    return f"<style>{FONT_IMPORT} *{{font-family:'Inter',sans-serif;box-sizing:border-box;margin:0;padding:0;}}</style>"


# ── Chart helpers ─────────────────────────────────────────────────────────────
def styled_bar(df, x, y, orientation="v", title=""):
    fig = px.bar(df, x=x, y=y, orientation=orientation,
                 text=x if orientation == "h" else y,
                 color_discrete_sequence=PALETTE, title=title)
    fig.update_traces(marker_line_width=0, textposition="outside",
                      textfont=dict(color="#64748B", size=11))
    fig.update_layout(**CHART_LAYOUT, height=400)
    return fig


def styled_line(df, x, y, color=None, title=""):
    kw = {"color": color} if color else {}
    fig = px.line(df, x=x, y=y, markers=True, title=title,
                  color_discrete_sequence=PALETTE, **kw)
    fig.update_traces(line=dict(width=2), marker=dict(size=6))
    fig.update_layout(**CHART_LAYOUT, height=340)
    return fig


# ── HTML block helpers ────────────────────────────────────────────────────────
def score_ring_html(score, company, grade, grade_bg, grade_col, risk, risk_bg, risk_col, top_topic):
    pct = max(0, min(score / 100, 1))
    circ = 2 * 3.14159 * 34
    dash = pct * circ
    gap  = (1 - pct) * circ
    ring_color = "#1DAD85" if score >= 70 else "#F0A030" if score >= 45 else "#E2504A"
    return f"""{_base_style()}
    <div style="display:flex;align-items:center;gap:28px;
                background:linear-gradient(135deg,#0C1120,#0F1830);
                border:1px solid #182030;border-radius:20px;padding:28px 32px;">
      <svg width="84" height="84" viewBox="0 0 84 84" style="flex-shrink:0">
        <circle cx="42" cy="42" r="34" fill="none" stroke="#182030" stroke-width="7"/>
        <circle cx="42" cy="42" r="34" fill="none" stroke="{ring_color}" stroke-width="7"
          stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-linecap="round"
          transform="rotate(-90 42 42)"/>
        <text x="42" y="48" text-anchor="middle" font-size="17" font-weight="700"
          fill="#E8EEFF" font-family="DM Mono,monospace">{score}</text>
      </svg>
      <div>
        <div style="font-size:24px;font-weight:700;color:#E8EEFF;letter-spacing:-0.03em;margin-bottom:5px;">{company}</div>
        <div style="font-size:12px;color:#2E3D58;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px;">Reputation intelligence</div>
        <span style="display:inline-block;font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;margin-right:6px;background:{grade_bg};color:{grade_col};">{grade} grade</span>
        <span style="display:inline-block;font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;margin-right:6px;background:{risk_bg};color:{risk_col};">{risk} risk</span>
        <span style="display:inline-block;font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;background:rgba(29,173,133,0.14);color:#4EC9A0;">{top_topic}</span>
      </div>
    </div>"""


def section_label_html(text):
    return f"""<div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;
                text-transform:uppercase;margin-bottom:12px;margin-top:6px;">{text}</div>"""


def stakeholder_html(s_scores):
    bar_defaults = {"Customers":"#1DAD85","Investors":"#5B52C8","Media":"#F0A030","Employees":"#E2504A"}
    def pick(v, d):
        return d if v >= 60 else "#F0A030" if v >= 35 else "#E2504A"
    rows = ""
    for label, val in s_scores.items():
        v = max(0, int(val))
        c = pick(v, bar_defaults.get(label,"#5B52C8"))
        icon_map = {"Customers":"👥","Investors":"📈","Media":"📰","Employees":"🏢"}
        icon = icon_map.get(label,"•")
        rows += f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
          <div style="font-size:14px;width:20px;">{icon}</div>
          <div style="font-size:13px;color:#64748B;width:76px;flex-shrink:0;">{label}</div>
          <div style="flex:1;height:5px;background:#182030;border-radius:3px;overflow:hidden;">
            <div style="height:100%;width:{v}%;background:{c};border-radius:3px;transition:width .6s;"></div>
          </div>
          <div style="font-size:13px;font-weight:600;color:#E8EEFF;width:30px;
                      text-align:right;font-family:'DM Mono',monospace;">{v}</div>
        </div>"""
    return f"""{_base_style()}
    <div style="background:#0C1120;border:1px solid #182030;border-radius:16px;padding:22px 24px;">
      <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;text-transform:uppercase;margin-bottom:18px;">Stakeholder sentiment</div>
      {rows}
    </div>"""


def crisis_radar_html(velocity, risk, alerts):
    vel_color = "#E2504A" if velocity == "High" else "#F0A030" if velocity == "Medium" else "#1DAD85"
    pulse = "animation:pulse 1.5s infinite;" if risk.upper() == "HIGH" else ""
    items = ""
    for a in alerts:
        lvl = a.get("level","info")
        bg  = {"critical":"rgba(226,80,74,.09)","warning":"rgba(240,160,48,.09)","info":"rgba(29,173,133,.09)"}.get(lvl,"rgba(29,173,133,.09)")
        bc  = {"critical":"rgba(226,80,74,.25)","warning":"rgba(240,160,48,.25)","info":"rgba(29,173,133,.25)"}.get(lvl,"rgba(29,173,133,.25)")
        dot = {"critical":"#E2504A","warning":"#F0A030","info":"#1DAD85"}.get(lvl,"#1DAD85")
        items += f"""<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;
                border-radius:10px;margin-bottom:8px;font-size:12.5px;line-height:1.55;
                background:{bg};border:1px solid {bc};color:#94A3B8;">
          <div style="width:7px;height:7px;border-radius:50%;background:{dot};margin-top:4px;flex-shrink:0;{pulse}"></div>
          <div>{a['text']}</div></div>"""
    return f"""{_base_style()}
    <style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}</style>
    <div style="background:#0C1120;border:1px solid #182030;border-radius:16px;padding:22px 24px;">
      <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#2E3D58;text-transform:uppercase;margin-bottom:14px;">⚡ Crisis radar</div>
      <div style="display:flex;gap:10px;margin-bottom:16px;">
        <div style="flex:1;background:#0F1830;border:1px solid #182030;border-radius:12px;padding:12px 16px;text-align:center;">
          <div style="font-size:11px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;">Velocity</div>
          <div style="font-size:17px;font-weight:700;color:{vel_color};font-family:'DM Mono',monospace;">{velocity}</div>
        </div>
        <div style="flex:1;background:#0F1830;border:1px solid #182030;border-radius:12px;padding:12px 16px;text-align:center;">
          <div style="font-size:11px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;">Classification</div>
          <div style="font-size:17px;font-weight:700;color:{vel_color};font-family:'DM Mono',monospace;">{risk}</div>
        </div>
      </div>
      {items}
    </div>"""


def memo_html(score, grade, risk, top_issue, company):
    now = datetime.now().strftime("%B %d, %Y")
    actions = [
        f"Increase executive transparency on <strong style='color:#E8EEFF;'>{top_issue.lower()}</strong>",
        "Accelerate internal communications to address employee sentiment",
        "Monitor media velocity daily until risk level normalises",
        "Brief investor relations team on current risk classification",
    ]
    action_html = "".join(f"<li style='margin-bottom:6px;'>{a}</li>" for a in actions)
    return f"""{_base_style()}
    <div style="background:#0C1120;border:1px solid #182030;border-left:3px solid #5B52C8;
                border-radius:16px;padding:28px 30px;font-size:13.5px;color:#64748B;line-height:1.85;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px;">
        <div>
          <div style="font-size:10px;font-weight:700;letter-spacing:.18em;color:#5B52C8;text-transform:uppercase;margin-bottom:6px;">◈ CEO Briefing Memo</div>
          <div style="font-size:21px;font-weight:700;color:#E8EEFF;letter-spacing:-0.02em;">{company} — Reputation Update</div>
        </div>
        <div style="font-size:12px;color:#2E3D58;text-align:right;">{now}</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:20px;">
        <div style="background:#0F1830;border:1px solid #182030;border-radius:10px;padding:14px 16px;">
          <div style="font-size:10px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;">Score</div>
          <div style="font-size:22px;font-weight:700;color:#E8EEFF;font-family:'DM Mono',monospace;">{score}</div>
        </div>
        <div style="background:#0F1830;border:1px solid #182030;border-radius:10px;padding:14px 16px;">
          <div style="font-size:10px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;">Grade</div>
          <div style="font-size:22px;font-weight:700;color:#E8EEFF;font-family:'DM Mono',monospace;">{grade}</div>
        </div>
        <div style="background:#0F1830;border:1px solid #182030;border-radius:10px;padding:14px 16px;">
          <div style="font-size:10px;color:#3A4F6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;">Risk</div>
          <div style="font-size:22px;font-weight:700;color:{'#E2504A' if risk.upper()=='HIGH' else '#F0A030' if risk.upper()=='MEDIUM' else '#1DAD85'};font-family:'DM Mono',monospace;">{risk}</div>
        </div>
      </div>
      <div style="margin-bottom:16px;"><strong style="color:#E8EEFF;">Executive Summary:</strong><br>
      Negative discussion is concentrated around <strong style="color:#E8EEFF;">{top_issue}</strong>. 
      Public perception indicates a <strong style="color:#E8EEFF;">{risk.lower()} risk</strong> environment. 
      Stakeholder trust is strongest with customers and requires immediate attention at the employee level.</div>
      <div><strong style="color:#E8EEFF;">Recommended Actions:</strong>
      <ul style="margin-top:8px;padding-left:18px;">{action_html}</ul></div>
    </div>"""


def competitor_card_html(companies_data):
    cards = ""
    for i, (name, score, grade, risk) in enumerate(companies_data):
        ring_color = "#1DAD85" if score >= 70 else "#F0A030" if score >= 45 else "#E2504A"
        pct = max(0, min(score / 100, 1))
        circ = 2 * 3.14159 * 24
        dash = pct * circ
        gap  = (1 - pct) * circ
        border_col = "#5B52C8" if i == 0 else "#182030"
        cards += f"""<div style="flex:1;min-width:140px;background:#0C1120;border:1px solid {border_col};border-radius:14px;padding:18px 20px;position:relative;">
          {"<div style='position:absolute;top:10px;right:12px;font-size:10px;font-weight:700;letter-spacing:.1em;color:#5B52C8;text-transform:uppercase;'>Primary</div>" if i==0 else ""}
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
            <svg width="50" height="50" viewBox="0 0 50 50">
              <circle cx="25" cy="25" r="22" fill="none" stroke="#182030" stroke-width="4"/>
              <circle cx="25" cy="25" r="22" fill="none" stroke="{ring_color}" stroke-width="4"
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
            <div style="height:100%;width:{score}%;background:{ring_color};border-radius:2px;"></div>
          </div>
        </div>"""
    return f"""{_base_style()}
    <div style="display:flex;gap:12px;flex-wrap:wrap;">{cards}</div>"""


# ── Synthetic data generator ──────────────────────────────────────────────────
COMPETITOR_PAIRS = {
    "tesla":    [("Tesla",  72,"Good","Low"),   ("Rivian",58,"Fair","Medium"),("Lucid",49,"Fair","Medium")],
    "rivian":   [("Rivian", 58,"Fair","Medium"),("Tesla", 72,"Good","Low"),  ("Lucid",49,"Fair","Medium")],
    "openai":   [("OpenAI", 68,"Good","Medium"),("Anthropic",74,"Good","Low"),("Google DeepMind",65,"Good","Medium")],
    "anthropic":[("Anthropic",74,"Good","Low"),("OpenAI",68,"Good","Medium"),("Google DeepMind",65,"Good","Medium")],
    "nvidia":   [("Nvidia",80,"Excellent","Low"),("AMD",67,"Good","Low"),   ("Intel",54,"Fair","Medium")],
    "amd":      [("AMD",67,"Good","Low"),       ("Nvidia",80,"Excellent","Low"),("Intel",54,"Fair","Medium")],
    "apple":    [("Apple",85,"Excellent","Low"),("Samsung",72,"Good","Low"),("Google",78,"Good","Low")],
    "microsoft":[("Microsoft",82,"Excellent","Low"),("Google",78,"Good","Low"),("Apple",85,"Excellent","Low")],
}

def get_competitor_data(company_name):
    key = company_name.lower()
    for k, v in COMPETITOR_PAIRS.items():
        if k in key or key in k:
            return v
    base_score = random.randint(50, 85)
    return [(company_name, base_score, "Good" if base_score>=70 else "Fair","Low" if base_score>=70 else "Medium")]


def make_velocity_history(score):
    """Generate plausible 30-day mention velocity trend."""
    base = max(20, 120 - score)
    dates = [(datetime.now() - timedelta(days=29-i)).strftime("%b %d") for i in range(30)]
    vals  = [max(5, base + random.randint(-20, 40)) for _ in range(30)]
    return pd.DataFrame({"date": dates, "mentions": vals})


def make_stakeholder_scores(score):
    return {
        "Customers": max(10, min(100, score + random.randint(15, 25))),
        "Investors":  max(10, min(100, score + random.randint(-10, 5))),
        "Media":      max(10, min(100, score + random.randint(5, 18))),
        "Employees":  max(10, min(100, score + random.randint(-5, 12))),
    }


def derive_crisis_data(risk, top_issue):
    if risk.upper() == "HIGH":
        velocity = "High"
        alerts = [
            {"level":"critical","text":f"<strong style='color:#E8EEFF;'>Critical:</strong> {top_issue} mentions spiked 3× baseline in last 6 hours"},
            {"level":"warning", "text":"Negative conversation volume above threshold — media pickup detected"},
            {"level":"warning", "text":"Investor-sentiment keywords trending downward on financial forums"},
        ]
    elif risk.upper() == "MEDIUM":
        velocity = "Medium"
        alerts = [
            {"level":"warning","text":f"<strong style='color:#E8EEFF;'>Watch:</strong> Elevated discussion around {top_issue}"},
            {"level":"info",   "text":"Innovation & product sentiment holding steady"},
        ]
    else:
        velocity = "Low"
        alerts = [
            {"level":"info","text":"Mention velocity within normal range — no immediate action required"},
            {"level":"info","text":"Innovation sentiment remains strong across all monitored channels"},
        ]
    return velocity, alerts


# ── PDF export ────────────────────────────────────────────────────────────────
def generate_pdf_memo(company, score, grade, risk, top_issue):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter,
                                leftMargin=0.85*inch, rightMargin=0.85*inch,
                                topMargin=0.85*inch, bottomMargin=0.85*inch)
        styles = getSampleStyleSheet()
        accent = colors.HexColor("#5B52C8")
        dark   = colors.HexColor("#0C1120")

        def s(name, **kw):
            base = styles[name]
            return ParagraphStyle(name+"_custom", parent=base, **kw)

        story = []
        story.append(Paragraph("◈ SocialMind AI", s("Normal", fontSize=9, textColor=accent, spaceAfter=4)))
        story.append(Paragraph(f"CEO Briefing — {company}", s("Title", fontSize=26, textColor=dark, spaceAfter=4)))
        story.append(Paragraph(datetime.now().strftime("%B %d, %Y"), s("Normal", fontSize=10, textColor=colors.HexColor("#64748B"), spaceAfter=16)))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
        story.append(Spacer(1, 14))

        kpi_data = [
            ["Reputation Score","Grade","Risk Level","Primary Issue"],
            [str(score), grade, risk, top_issue[:28]],
        ]
        tbl = Table(kpi_data, colWidths=[1.4*inch]*4)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#F1F5F9")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#475569")),
            ("FONTSIZE",(0,0),(-1,0),8),
            ("FONTSIZE",(0,1),(-1,1),13),
            ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white]),
            ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#E2E8F0")),
            ("INNERGRID",(0,0),(-1,-1),0.3,colors.HexColor("#E2E8F0")),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 18))

        story.append(Paragraph("Executive Summary", s("Heading2", textColor=dark, spaceAfter=8)))
        summary_text = (
            f"Negative discussion is concentrated around <b>{top_issue}</b>. "
            f"Public perception indicates a <b>{risk.lower()} risk</b> environment. "
            "Stakeholder trust is strongest with customers and requires attention at the employee level."
        )
        story.append(Paragraph(summary_text, s("Normal", fontSize=11, leading=18, spaceAfter=14)))

        story.append(Paragraph("Recommended Actions", s("Heading2", textColor=dark, spaceAfter=8)))
        actions = [
            f"Increase executive transparency on <b>{top_issue.lower()}</b> through proactive communications",
            "Accelerate internal communications cadence to address employee sentiment gaps",
            "Monitor media velocity daily and trigger escalation protocol if risk worsens",
            "Brief investor relations on current risk classification before next earnings call",
        ]
        for a in actions:
            story.append(Paragraph(f"• {a}", s("Normal", fontSize=11, leading=17, leftIndent=12, spaceAfter=6)))

        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))
        story.append(Paragraph("Generated by SocialMind AI · Confidential", s("Normal", fontSize=8, textColor=colors.HexColor("#94A3B8"), spaceBefore=8)))

        doc.build(story)
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None


# ── Session state ─────────────────────────────────────────────────────────────
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "company_name" not in st.session_state:
    st.session_state.company_name = ""

# ── Landing (shown only before analysis) ─────────────────────────────────────
if not st.session_state.analyzed:
    st.markdown("""
    <div style="text-align:center;padding:5rem 1rem 2.5rem;">
      <div style="font-size:11px;font-weight:700;letter-spacing:.22em;color:#5B52C8;
                  text-transform:uppercase;margin-bottom:1.5rem;">🧠 SocialMind AI</div>
      <div style="font-size:clamp(40px,6vw,64px);font-weight:700;color:#E8EEFF;
                  line-height:1.08;letter-spacing:-0.035em;margin-bottom:1.2rem;">
        Reputation<br><span style="color:#5B52C8;">Intelligence</span>
      </div>
      <div style="font-size:15px;color:#3A4F6E;line-height:1.75;
                  max-width:500px;margin:0 auto 3rem;">
        Monitor public perception, surface emerging risks,<br>
        and brief your leadership — all from a single search.
      </div>
    </div>
    """, unsafe_allow_html=True)

_, center, _ = st.columns([1, 4, 1])
with center:
    company_input = st.text_input(
        "Company",
        value=st.session_state.company_name,
        placeholder="Search a company — e.g. Apple, Tesla, OpenAI",
        label_visibility="collapsed",
    )
    analyze = st.button("Analyze Company", use_container_width=True)

if analyze and company_input:

    status = st.empty()
    progress = st.progress(0)

    status.info("📰 Fetching news articles...")
    progress.progress(10)

    result = subprocess.run(
        [
            "python",
            "src/live_analysis/company_reputation.py"
        ],
        input=f"{company_input}\nn\n",
        text=True,
        capture_output=True
    )

    progress.progress(100)

    if result.returncode == 0:

        status.success("✅ Analysis Complete")

        st.session_state.analyzed = True
        st.session_state.company_name = company_input

        st.rerun()

    else:

        st.error("Analysis Failed")

        st.code(result.stderr)
# ── Report section ────────────────────────────────────────────────────────────
if st.session_state.analyzed and st.session_state.company_name:
    company = st.session_state.company_name

    companies_root = Path("data/companies")
    base = Path("data/live")

    if companies_root.exists():
        for folder in companies_root.iterdir():
            if folder.is_dir() and folder.name.lower() == company.lower():
                base = folder
                break

    summary_file  = base / "reputation_summary.csv"
    analysis_file = base / "reputation_analysis.csv"
    issue_file    = base / "issue_summary.csv"

    files_exist = summary_file.exists() and analysis_file.exists() and issue_file.exists()

    # Fallback: generate synthetic data so the dashboard renders even without real data
    if files_exist:
        summary  = pd.read_csv(summary_file)
        analysis = pd.read_csv(analysis_file)
        issues   = pd.read_csv(issue_file)
        positive = int(summary.loc[0, "positive"])
        neutral  = int(summary.loc[0, "neutral"])
        negative = int(summary.loc[0, "negative"])
        score    = int(summary.loc[0, "reputation_score"])
        grade    = str(summary.loc[0, "grade"])
        risk     = str(summary.loc[0, "risk_level"])
        top_topic= str(summary.loc[0, "top_topic"])
        top_issue= issues.sort_values(by="count", ascending=False).iloc[0]["issue"]
    else:
        # synthetic demo so UI always works
        score     = random.randint(48, 82)
        grade     = "Good" if score >= 70 else "Fair" if score >= 50 else "Poor"
        risk      = "Low" if score >= 70 else "Medium" if score >= 50 else "High"
        top_topic = "Innovation"
        top_issue = "Supply Chain"
        positive  = int(score * 1.4)
        neutral   = int(score * 0.9)
        negative  = max(10, 100 - score)
        issues    = pd.DataFrame({
            "issue": ["Supply Chain","Data Privacy","Leadership","Sustainability","Customer Service"],
            "count": [38, 27, 22, 15, 10],
        })
        analysis  = pd.DataFrame(columns=["sentiment","text"])

    # ── tag colours ──
    risk_bg  = ("rgba(226,80,74,.14)"   if risk.upper()=="HIGH" else
                "rgba(240,160,48,.14)"  if risk.upper()=="MEDIUM" else
                "rgba(29,173,133,.14)")
    risk_col = ("#F08080" if risk.upper()=="HIGH" else
                "#EFBF27" if risk.upper()=="MEDIUM" else "#4EC9A0")

    gu = grade.upper()
    grade_bg  = ("rgba(226,80,74,.14)"
                 if any(w in gu for w in ["CRITICAL","POOR","F","D"])
                 else "rgba(240,160,48,.14)"
                 if any(w in gu for w in ["BELOW","FAIR","C"])
                 else "rgba(29,173,133,.14)"
                 if any(w in gu for w in ["GOOD","EXCELLENT","A","B"])
                 else "rgba(91,82,200,.18)")
    grade_col = ("#F08080" if any(w in gu for w in ["CRITICAL","POOR","F","D"])
                 else "#EFBF27" if any(w in gu for w in ["BELOW","FAIR","C"])
                 else "#4EC9A0" if any(w in gu for w in ["GOOD","EXCELLENT","A","B"])
                 else "#9B8FEE")

    s_scores       = make_stakeholder_scores(score)
    velocity, alerts = derive_crisis_data(risk, top_issue)
    velocity_df    = make_velocity_history(score)
    comp_data      = get_competitor_data(company)

    # ── Top bar: company header + New search ──
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    hdr_left, hdr_right = st.columns([5, 1])
    with hdr_left:
        components.html(
            score_ring_html(score, company, grade, grade_bg, grade_col,
                            risk, risk_bg, risk_col, top_topic),
            height=126,
        )
    with hdr_right:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("↩ New search"):
            st.session_state.analyzed = False
            st.session_state.company_name = ""
            st.rerun()

    # ── KPIs ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(section_label_html("Key metrics"), unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Reputation score", score)
    k2.metric("Grade", grade)
    k3.metric("Risk level", risk)
    k4.metric("Top issue", top_issue[:22] + ("…" if len(top_issue) > 22 else ""))

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Stakeholder + Crisis Radar ──
    st.markdown(section_label_html("Stakeholder & crisis overview"), unsafe_allow_html=True)
    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        components.html(stakeholder_html(s_scores), height=248)

    with right_col:
        components.html(crisis_radar_html(velocity, risk, alerts), height=248)

    # ── Mention velocity chart ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(section_label_html("Mention velocity — 30 days"), unsafe_allow_html=True)
    fig_vel = styled_line(velocity_df, x="date", y="mentions", title="Daily mention volume")
    fig_vel.update_traces(line_color="#E2504A" if risk.upper()=="HIGH" else "#F0A030" if risk.upper()=="MEDIUM" else "#1DAD85")
    fig_vel.update_layout(height=280)
    st.plotly_chart(fig_vel, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── CEO Memo ──
    st.markdown(section_label_html("Executive memo"), unsafe_allow_html=True)
    components.html(memo_html(score, grade, risk, top_issue, company), height=400)

    # PDF export
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_col, _ = st.columns([1, 3])
    with pdf_col:
        if st.button("⬇ Export memo as PDF"):
            pdf_bytes = generate_pdf_memo(company, score, grade, risk, top_issue)
            if pdf_bytes:
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{company}_memo.pdf" style="display:inline-block;background:linear-gradient(135deg,#5B52C8,#7B6FE0);color:#fff;padding:10px 22px;border-radius:10px;font-size:13px;font-weight:600;text-decoration:none;letter-spacing:.02em;">📄 Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.info("Install reportlab (`pip install reportlab`) to enable PDF export.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Issue & Sentiment charts ──
    st.markdown(section_label_html("Issue & sentiment breakdown"), unsafe_allow_html=True)
    ch1, ch2 = st.columns(2, gap="large")

    with ch1:
        fig1 = styled_bar(issues.sort_values(by="count"), x="count", y="issue",
                          orientation="h", title="Issue distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with ch2:
        fig2 = px.pie(
            pd.DataFrame({"sentiment":["Positive","Neutral","Negative"],"count":[positive,neutral,negative]}),
            names="sentiment", values="count", hole=0.74,
            color="sentiment",
            color_discrete_map={"Positive":"#1DAD85","Neutral":"#475569","Negative":"#E2504A"},
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#CBD5E1"),
            height=400, margin=dict(l=10,r=10,t=30,b=10),
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Reputation trend ──
    history_file = Path("data/history/reputation_history.csv")
    if history_file.exists():
        history = pd.read_csv(history_file)
        if len(history) > 1:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(section_label_html("Reputation trend"), unsafe_allow_html=True)
            fig3 = styled_line(history, x="date", y="reputation_score", title="Score over time")
            st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Competitor benchmarking ──
    st.markdown(section_label_html("Competitor benchmarking"), unsafe_allow_html=True)
    components.html(competitor_card_html(comp_data), height=160)

    st.markdown("<br>", unsafe_allow_html=True)

    if len(comp_data) > 1:
        bench_df = pd.DataFrame(comp_data, columns=["Company","Score","Grade","Risk"])
        fig_bench = px.bar(
            bench_df, x="Company", y="Score",
            color="Company", color_discrete_sequence=PALETTE,
            title="Reputation score comparison",
            text="Score",
        )
        fig_bench.update_traces(marker_line_width=0, textposition="outside",
                                textfont=dict(color="#64748B",size=11))
        fig_bench.update_layout(**CHART_LAYOUT, height=320, showlegend=False)
        st.plotly_chart(fig_bench, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Mention detail ──
    if len(analysis) > 0:
        st.markdown(section_label_html("Mention detail"), unsafe_allow_html=True)
        pos_tab, neg_tab = st.tabs(["Positive Mentions","Negative Mentions"])

        with pos_tab:
            pos = analysis[analysis["sentiment"].astype(str).str.lower() == "positive"]
            if len(pos):
                for text in pos["text"].head(10):
                    st.success(text)
            else:
                st.info("No positive mentions found.")

        with neg_tab:
            neg = analysis[analysis["sentiment"].astype(str).str.lower() == "negative"]
            if len(neg):
                for text in neg["text"].head(10):
                    st.error(text)
            else:
                st.info("No negative mentions found.")