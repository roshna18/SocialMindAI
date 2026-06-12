import streamlit as st
import streamlit.components.v1 as components
import subprocess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="SocialMind AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# GLOBAL STYLES  (injected once via st.markdown)
# ─────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stAppViewContainer"] { background: #080D1A; }
.block-container { max-width: 1160px; padding: 2.5rem 2rem 4rem; }
* { font-family: 'Inter', sans-serif !important; }

/* search */
div[data-testid="stTextInput"] input {
    background: #111827 !important; border: 1px solid #1F2B45 !important;
    border-radius: 12px !important; color: #F1F0FF !important;
    font-size: 15px !important; padding: 14px 18px !important; height: auto !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #534AB7 !important;
    box-shadow: 0 0 0 3px rgba(83,74,183,0.15) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #3D4E68 !important; }
div[data-testid="stTextInput"] label { display: none !important; }

/* button */
div[data-testid="stButton"] > button {
    background: #534AB7 !important; color: #F1F0FF !important;
    border: none !important; border-radius: 10px !important;
    font-size: 14px !important; font-weight: 500 !important;
    padding: 12px 28px !important; height: auto !important; width: 100%;
}
div[data-testid="stButton"] > button:hover { background: #6B62C9 !important; }

/* metrics */
[data-testid="stMetric"] {
    background: #0F1829 !important; border: 1px solid #1A2640 !important;
    border-radius: 14px !important; padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] { color: #3D4E68 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] {
    color: #F1F0FF !important; font-size: 24px !important;
    font-family: 'DM Mono', monospace !important;
}

/* expanders */
[data-testid="stExpander"] {
    background: #0F1829 !important; border: 1px solid #1A2640 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: #94A3B8 !important; font-size: 14px !important; font-weight: 500 !important; }

/* divider */
hr { border: none; border-top: 1px solid #1A2236 !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#64748B", size=12),
    margin=dict(l=0, r=0, t=32, b=0),
    xaxis=dict(gridcolor="#1A2640", linecolor="#1A2640", tickfont=dict(color="#64748B")),
    yaxis=dict(gridcolor="#1A2640", linecolor="#1A2640", tickfont=dict(color="#64748B")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B")),
)
PALETTE = ["#534AB7", "#1D9E75", "#EF9F27", "#E24B4A", "#9B95E8", "#4EC9A0"]


def styled_bar(df, x, y, orientation="v", title=""):
    fig = px.bar(df, x=x, y=y, orientation=orientation,
                 text=x if orientation == "h" else y,
                 color_discrete_sequence=PALETTE, title=title)
    fig.update_traces(marker_line_width=0, textposition="outside",
                      textfont=dict(color="#64748B", size=11))
    fig.update_layout(**CHART_LAYOUT, height=400)
    return fig


def styled_line(df, x, y, title=""):
    fig = px.line(df, x=x, y=y, markers=True, title=title,
                  color_discrete_sequence=["#534AB7"])
    fig.update_traces(line=dict(width=2),
                      marker=dict(size=6, color="#534AB7",
                                  line=dict(color="#9B95E8", width=1.5)))
    fig.update_layout(**CHART_LAYOUT, height=320)
    return fig


# ─────────────────────────────────────────
# HTML BLOCK HELPERS  (fully self-contained, no external CSS classes)
# ─────────────────────────────────────────

FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=DM+Mono:wght@500&display=swap');"

def _base_style():
    return f"<style>{FONT_IMPORT} * {{font-family:'Inter',sans-serif;box-sizing:border-box;margin:0;padding:0;}}</style>"


def score_ring_html(score, company, grade, grade_tag_color, grade_text_color,
                    risk, risk_tag_color, risk_text_color, top_topic):
    pct = max(0, min(score / 100, 1))
    circ = 2 * 3.14159 * 34
    dash, gap = pct * circ, (1 - pct) * circ
    ring_color = "#1D9E75" if score >= 70 else "#EF9F27" if score >= 45 else "#E24B4A"

    return f"""
    {_base_style()}
    <div style="display:flex;align-items:center;gap:24px;
                background:#0F1829;border:1px solid #1A2640;border-radius:16px;
                padding:24px 28px;">
      <svg width="80" height="80" viewBox="0 0 80 80" style="flex-shrink:0">
        <circle cx="40" cy="40" r="34" fill="none" stroke="#1A2640" stroke-width="6"/>
        <circle cx="40" cy="40" r="34" fill="none" stroke="{ring_color}" stroke-width="6"
          stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-linecap="round"
          transform="rotate(-90 40 40)"/>
        <text x="40" y="46" text-anchor="middle" font-size="17" font-weight="600"
          fill="#F1F0FF" font-family="DM Mono,monospace">{score}</text>
      </svg>
      <div>
        <div style="font-size:22px;font-weight:600;color:#F1F0FF;letter-spacing:-0.02em;margin-bottom:4px;">
          {company}
        </div>
        <div style="font-size:13px;color:#3D4E68;margin-bottom:10px;">
          Reputation intelligence report
        </div>
        <span style="display:inline-block;font-size:11px;font-weight:500;padding:3px 10px;
               border-radius:20px;margin-right:6px;
               background:{grade_tag_color};color:{grade_text_color};">
          {grade} grade
        </span>
        <span style="display:inline-block;font-size:11px;font-weight:500;padding:3px 10px;
               border-radius:20px;margin-right:6px;
               background:{risk_tag_color};color:{risk_text_color};">
          {risk} risk
        </span>
        <span style="display:inline-block;font-size:11px;font-weight:500;padding:3px 10px;
               border-radius:20px;background:rgba(29,158,117,0.15);color:#4EC9A0;">
          {top_topic}
        </span>
      </div>
    </div>
    """


def stakeholder_html(s_scores):
    bar_defaults = {
        "Customers": "#1D9E75",
        "Investors": "#534AB7",
        "Media":     "#EF9F27",
        "Employees": "#E24B4A",
    }
    def pick_color(val, default):
        if val >= 60: return default
        if val >= 35: return "#EF9F27"
        return "#E24B4A"

    rows = ""
    for label, val in s_scores.items():
        v = max(0, val)
        color = pick_color(v, bar_defaults.get(label, "#534AB7"))
        rows += f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
          <div style="font-size:13px;color:#64748B;width:80px;flex-shrink:0;">{label}</div>
          <div style="flex:1;height:6px;background:#1A2640;border-radius:3px;overflow:hidden;">
            <div style="height:100%;width:{v}%;background:{color};border-radius:3px;"></div>
          </div>
          <div style="font-size:13px;font-weight:500;color:#F1F0FF;width:28px;
                      text-align:right;font-family:'DM Mono',monospace;">{v}</div>
        </div>
        """
    return f"""
    {_base_style()}
    <div style="background:#0F1829;border:1px solid #1A2640;border-radius:14px;padding:22px 24px;">
      <div style="font-size:11px;font-weight:600;letter-spacing:0.12em;color:#3D4E68;
                  text-transform:uppercase;margin-bottom:16px;">Stakeholder sentiment</div>
      {rows}
    </div>
    """


def alerts_html(top_issue, risk):
    items = f"""
    <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 16px;
                border-radius:10px;margin-bottom:8px;font-size:13px;line-height:1.5;
                background:rgba(226,75,74,0.08);border:1px solid rgba(226,75,74,0.2);color:#F08080;">
      <div style="width:8px;height:8px;border-radius:50%;background:#E24B4A;
                  margin-top:4px;flex-shrink:0;"></div>
      <div>Investor concern rising around <strong style="color:#F1F0FF;">{top_issue}</strong></div>
    </div>
    """
    if str(risk).upper() == "HIGH":
        items += """
    <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 16px;
                border-radius:10px;margin-bottom:8px;font-size:13px;line-height:1.5;
                background:rgba(239,159,39,0.08);border:1px solid rgba(239,159,39,0.2);color:#EFBF27;">
      <div style="width:8px;height:8px;border-radius:50%;background:#EF9F27;
                  margin-top:4px;flex-shrink:0;"></div>
      <div>Negative conversation volume above baseline threshold</div>
    </div>
        """
    items += """
    <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 16px;
                border-radius:10px;font-size:13px;line-height:1.5;
                background:rgba(29,158,117,0.08);border:1px solid rgba(29,158,117,0.2);color:#4EC9A0;">
      <div style="width:8px;height:8px;border-radius:50%;background:#1D9E75;
                  margin-top:4px;flex-shrink:0;"></div>
      <div>Innovation sentiment remains stable</div>
    </div>
    """
    return f"""
    {_base_style()}
    <div style="background:#0F1829;border:1px solid #1A2640;border-radius:14px;padding:18px 20px;">
      <div style="font-size:11px;font-weight:600;letter-spacing:0.12em;color:#3D4E68;
                  text-transform:uppercase;margin-bottom:14px;">Live risk alerts</div>
      {items}
    </div>
    """


def memo_html(score, grade, risk, top_issue):
    return f"""
    {_base_style()}
    <div style="background:#0F1829;border:1px solid #1A2640;border-left:3px solid #534AB7;
                border-radius:14px;padding:24px 26px;font-size:14px;color:#94A3B8;line-height:1.8;">
      <div style="font-size:11px;font-weight:600;letter-spacing:0.12em;color:#534AB7;
                  text-transform:uppercase;margin-bottom:14px;">◈ CEO briefing</div>
      <strong style="color:#F1F0FF;">Reputation score:</strong> {score} ({grade})<br><br>
      <strong style="color:#F1F0FF;">Primary risk factor:</strong> {top_issue}<br><br>
      Negative discussion is concentrated around
      <strong style="color:#F1F0FF;">{top_issue}</strong>.
      Public perception currently indicates a
      <strong style="color:#F1F0FF;">{risk.lower()} risk</strong> environment.
      Stakeholder trust is strongest with customers and weakest with employees
      based on current signal volume.<br><br>
      <strong style="color:#F1F0FF;">Recommended actions:</strong>
      Increase executive transparency on {top_issue.lower()},
      accelerate internal communications to address employee sentiment,
      and monitor media velocity daily until risk level normalises.
    </div>
    """


def section_label_html(text):
    return f"""
    <div style="font-size:11px;font-weight:600;letter-spacing:0.12em;color:#3D4E68;
                text-transform:uppercase;margin-bottom:10px;margin-top:4px;">{text}</div>
    """


# ─────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────

st.markdown("""
<div style="text-align:center;padding:4rem 1rem 2rem;">
  <div style="font-size:13px;font-weight:500;letter-spacing:0.18em;color:#534AB7;
              text-transform:uppercase;margin-bottom:1.5rem;">
      🧠 SocialMind AI
  </div>

  <div style="font-size:clamp(38px,6vw,60px);font-weight:600;color:#F1F0FF;
              line-height:1.1;letter-spacing:-0.03em;margin-bottom:1rem;">
      Reputation<br>
      <span style="color:#534AB7;">Intelligence</span>
  </div>

  <div style="font-size:16px;color:#64748B;line-height:1.7;
              max-width:520px;margin:0 auto 2.5rem;">
      Monitor public perception, surface emerging risks,
      and brief your leadership — all from a single search.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>

.stTextInput input{
    height:58px !important;
    border-radius:16px !important;
    border:1px solid #232B44 !important;
    background:#0F172A !important;
    color:#F8FAFC !important;
    font-size:16px !important;
}

div.stButton > button{
    height:58px !important;
    border-radius:16px !important;
    background:#534AB7 !important;
    color:white !important;
    border:none !important;
    font-weight:600 !important;
    font-size:15px !important;
    width:100% !important;
}

</style>
""", unsafe_allow_html=True)

left, center, right = st.columns([1, 4, 1])

with center:

    company = st.text_input(
        "Company",
        placeholder="Search a company — e.g. Apple, Tesla, OpenAI",
        label_visibility="collapsed"
    )

    analyze = st.button(
        "Analyze Company",
        use_container_width=True
    )

# ─────────────────────────────────────────
# RUN ANALYSIS
# ─────────────────────────────────────────

if analyze and company:

    with st.spinner(
        f"Pulling intelligence on {company}..."
    ):

        subprocess.run(
            [
                "python",
                "src/live_analysis/company_reputation.py"
            ],
            input=f"{company}\nn\n",
            text=True
        )

    st.success(
        f"Analysis complete for {company}"
    )
# ─────────────────────────────────────────
# LOAD & RENDER REPORT
# ─────────────────────────────────────────

if company:

    companies_root = Path("data/companies")

    base = Path("data/live")

    if companies_root.exists():

        for folder in companies_root.iterdir():

            if (
                folder.is_dir()
                and folder.name.lower() == company.lower()
            ):
                base = folder
                break

    summary_file = base / "reputation_summary.csv"
    analysis_file = base / "reputation_analysis.csv"
    issue_file = base / "issue_summary.csv"

if company and companies_root.exists():

    for folder in companies_root.iterdir():

        if (
            folder.is_dir()
            and folder.name.lower() == company.lower()
        ):
            base = folder
            break

    summary_file  = base / "reputation_summary.csv"
    analysis_file = base / "reputation_analysis.csv"
    issue_file    = base / "issue_summary.csv"

    if summary_file.exists() and analysis_file.exists() and issue_file.exists():

        summary  = pd.read_csv(summary_file)
        analysis = pd.read_csv(analysis_file)
        issues   = pd.read_csv(issue_file)
        positive = int(summary.loc[0, "positive"])
        neutral = int(summary.loc[0, "neutral"])
        negative = int(summary.loc[0, "negative"])
        score     = int(summary.loc[0, "reputation_score"])
        grade     = str(summary.loc[0, "grade"])
        risk      = str(summary.loc[0, "risk_level"])
        top_topic = str(summary.loc[0, "top_topic"])
        top_issue = (
            issues.sort_values(by="count", ascending=False).iloc[0]["issue"]
        )

        # tag colours
        risk_tag_bg   = ("rgba(226,75,74,0.15)"   if risk.upper() == "HIGH"
                         else "rgba(239,159,39,0.15)" if risk.upper() == "MEDIUM"
                         else "rgba(29,158,117,0.15)")
        risk_text_col = ("#F08080" if risk.upper() == "HIGH"
                         else "#EFBF27" if risk.upper() == "MEDIUM"
                         else "#4EC9A0")

        gu = grade.upper()
        grade_tag_bg   = ("rgba(226,75,74,0.15)"
                          if any(w in gu for w in ["CRITICAL","POOR","F","D"])
                          else "rgba(239,159,39,0.15)"
                          if any(w in gu for w in ["BELOW","FAIR","C"])
                          else "rgba(29,158,117,0.15)"
                          if any(w in gu for w in ["GOOD","EXCELLENT","A","B"])
                          else "rgba(83,74,183,0.18)")
        grade_text_col = ("#F08080"
                          if any(w in gu for w in ["CRITICAL","POOR","F","D"])
                          else "#EFBF27"
                          if any(w in gu for w in ["BELOW","FAIR","C"])
                          else "#4EC9A0"
                          if any(w in gu for w in ["GOOD","EXCELLENT","A","B"])
                          else "#9B95E8")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Company header ──
        components.html(
            score_ring_html(score, company, grade,
                            grade_tag_bg, grade_text_col,
                            risk, risk_tag_bg, risk_text_col, top_topic),
            height=120,
        )

        # ── KPI metrics ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(section_label_html("Key metrics"), unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Reputation score", score)
        k2.metric("Grade", grade)
        k3.metric("Risk level", risk)
        k4.metric("Top issue", top_issue[:22] + ("…" if len(top_issue) > 22 else ""))

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Stakeholder + Alerts side by side ──
        left_col, right_col = st.columns([1, 1], gap="large")

        s_scores = {
        "Customers": max(10, min(100, score + 20)),
        "Investors": max(10, min(100, score - 5)),
        "Media": max(10, min(100, score + 10)),
        "Employees": max(10, min(100, score + 5)),
        }

        with left_col:
            components.html(stakeholder_html(s_scores), height=230)

        with right_col:
            alert_h = 220
            components.html(alerts_html(top_issue, risk), height=alert_h)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Executive memo ──
        st.markdown(section_label_html("Executive memo"), unsafe_allow_html=True)
        components.html(memo_html(score, grade, risk, top_issue), height=320)

        st.markdown("<hr>", unsafe_allow_html=True)

      # ── Charts ─────────────────────────────────────────────

        st.markdown(
            section_label_html(
                "Issue & sentiment breakdown"
            ),
            unsafe_allow_html=True
        )

        ch1, ch2 = st.columns(
            2,
            gap="large"
        )

        # ISSUE DISTRIBUTION

        with ch1:

            fig1 = styled_bar(
                issues.sort_values(
                    by="count"
                ),
                x="count",
                y="issue",
                orientation="h",
                title="Issue distribution"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        # SENTIMENT DONUT

        with ch2:

            sentiment_counts = pd.DataFrame({
                "sentiment": [
                    "Positive",
                    "Neutral",
                    "Negative"
                ],
                "count": [
                    positive,
                    neutral,
                    negative
                ]
            })

            fig2 = px.pie(
                sentiment_counts,
                names="sentiment",
                values="count",
                hole=0.75,
                color="sentiment",
                color_discrete_map={
                    "Positive": "#1D9E75",
                    "Neutral": "#64748B",
                    "Negative": "#E24B4A"
                }
            )

            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="Inter",
                    color="#CBD5E1"
                ),
                height=430,
                margin=dict(
                    l=10,
                    r=10,
                    t=30,
                    b=10
                ),
                legend=dict(
                    orientation="h",
                    y=-0.15
                )
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

# ── Trend ──

history_file = Path(
    "data/history/reputation_history.csv"
)

if history_file.exists():

    history = pd.read_csv(
        history_file
    )

    if len(history) > 1:

        st.markdown(
            "<hr>",
            unsafe_allow_html=True
        )

        st.markdown(
            section_label_html(
                "Reputation trend"
            ),
            unsafe_allow_html=True
        )

        fig3 = styled_line(
            history,
            x="date",
            y="reputation_score",
            title="Score over time"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )
# ── Mention Detail ───────────────────────────────────

if "analysis" in locals():

    st.markdown(
        "<hr>",
        unsafe_allow_html=True
    )

    st.markdown(
        section_label_html(
            "Mention detail"
        ),
        unsafe_allow_html=True
    )

    pos_tab, neg_tab = st.tabs(
        [
            "Positive Mentions",
            "Negative Mentions"
        ]
    )

    with pos_tab:

        pos = analysis[
            analysis["sentiment"]
            .astype(str)
            .str.lower()
            == "positive"
        ]

        if len(pos):

            for text in pos["text"].head(10):

                st.success(text)

        else:

            st.info(
                "No positive mentions found."
            )

    with neg_tab:

        neg = analysis[
            analysis["sentiment"]
            .astype(str)
            .str.lower()
            == "negative"
        ]

        if len(neg):

            for text in neg["text"].head(10):

                st.error(text)

        else:

            st.info(
                "No negative mentions found."
            )