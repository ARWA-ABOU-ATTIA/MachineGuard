import math
import os

import requests
import streamlit as st

import html
# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="MachineGuard | Failure Risk Assessment",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Design tokens
NAVY = "#0B1F33"
STEEL = "#4A6580"
TEAL = "#0E9AA7"
GREEN = "#1E8E5A"
RED = "#C8372D"
BORDER = "#D5DDE6"
BG = "#EEF1F5"


# --------------------------------------------------
# 2. Styling
# --------------------------------------------------

st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    html, body, .stApp, [class*="css"] {{
        font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', Roboto, sans-serif;
    }}
    .stApp {{ background-color: {BG}; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    #MainMenu, footer {{ visibility: hidden; }}

    .block-container {{
        max-width: 1180px;
        padding-top: 1.25rem;
        padding-bottom: 3rem;
    }}

    /* Header */
    .mg-header {{
        display: flex; flex-wrap: wrap; align-items: center;
        justify-content: space-between; gap: 1rem;
        background: {NAVY}; color: #fff;
        padding: 1.1rem 1.5rem; border-radius: 8px;
        border-bottom: 3px solid {TEAL};
        margin-bottom: 1.5rem;
    }}
    .mg-brand {{ display: flex; align-items: center; gap: 0.9rem; }}
    .mg-brand h1 {{
        color: #fff; font-size: 1.5rem; font-weight: 700;
        margin: 0; padding: 0; line-height: 1.2; letter-spacing: 0.2px;
    }}
    .mg-brand p {{ color: #AFC3D6; margin: 0; font-size: 0.9rem; }}
    .mg-meta {{ display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; }}
    .mg-pill {{
        display: inline-flex; align-items: center; gap: 0.5rem;
        border: 1px solid rgba(255,255,255,0.22); border-radius: 999px;
        padding: 0.3rem 0.8rem; font-size: 0.82rem; color: #E6EEF6;
    }}
    .mg-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
    .mg-dot.on {{ background: #3DDC97; box-shadow: 0 0 0 3px rgba(61,220,151,0.25); }}
    .mg-dot.off {{ background: #FF6B5E; box-shadow: 0 0 0 3px rgba(255,107,94,0.25); }}

    /* Panels */
    .mg-panel-title {{
        color: {NAVY}; font-size: 1.05rem; font-weight: 600;
        margin: 0 0 0.15rem 0;
    }}
    .mg-panel-sub {{ color: {STEEL}; font-size: 0.88rem; margin-bottom: 0.9rem; }}

    div[data-testid="stForm"] {{
        background: #fff; border: 1px solid {BORDER};
        border-radius: 8px; padding: 1.4rem 1.5rem;
    }}
    div[data-testid="stForm"] label p {{ color: {NAVY}; font-weight: 500; }}
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div {{ border-color: {BORDER}; }}
    div[data-testid="stNumberInput"] input:focus {{ border-color: {TEAL}; }}

    .mg-group {{
        color: {NAVY}; font-weight: 600; font-size: 0.98rem;
        padding-bottom: 0.4rem; margin-bottom: 0.6rem;
        border-bottom: 1px solid {BORDER};
    }}

    /* Primary button */
    div[data-testid="stFormSubmitButton"] button {{
        background: {TEAL}; border: none; color: #fff;
        font-weight: 600; font-size: 1.02rem;
        padding: 0.7rem 1rem; border-radius: 6px;
    }}
    div[data-testid="stFormSubmitButton"] button:hover {{ background: #0B7F8A; color: #fff; }}
    div[data-testid="stFormSubmitButton"] button:focus-visible {{
        outline: 3px solid rgba(14,154,167,0.4); outline-offset: 2px;
    }}

    /* Result */
    .mg-result {{
        background: #fff; border: 1px solid {BORDER};
        border-left-width: 6px; border-radius: 8px;
        padding: 1.4rem 1.6rem; margin-top: 1.5rem;
    }}
    .mg-result.fail {{ border-left-color: {RED}; }}
    .mg-result.ok {{ border-left-color: {GREEN}; }}
    .mg-result-grid {{
        display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;
    }}
    .mg-gauge {{ flex: 0 0 280px; max-width: 100%; }}
    .mg-gauge svg {{ width: 100%; height: auto; display: block; }}
    .mg-verdict {{ flex: 1 1 280px; }}
    .mg-status {{ font-size: 1.6rem; font-weight: 700; margin: 0 0 0.4rem 0; }}
    .mg-status.fail {{ color: {RED}; }}
    .mg-status.ok {{ color: {GREEN}; }}
    .mg-verdict p {{ color: #33475B; margin: 0 0 0.8rem 0; font-size: 0.96rem; line-height: 1.5; }}
    .mg-stats {{ display: flex; flex-wrap: wrap; gap: 0.8rem; }}
    .mg-stat {{
        flex: 1 1 120px; background: {BG};
        border-radius: 6px; padding: 0.6rem 0.8rem;
    }}
    .mg-stat span {{ display: block; color: {STEEL}; font-size: 0.8rem; }}
    .mg-stat strong {{ color: {NAVY}; font-size: 1.15rem; font-weight: 600; }}

    /* Summary table */
    table.mg-table {{
        width: 100%; border-collapse: collapse; background: #fff;
        border: 1px solid {BORDER}; border-radius: 8px; overflow: hidden;
        font-size: 0.92rem;
    }}
    table.mg-table th {{
        background: {BG}; color: {NAVY}; text-align: left;
        font-weight: 600; padding: 0.55rem 0.8rem;
    }}
    table.mg-table td {{ padding: 0.5rem 0.8rem; border-top: 1px solid {BORDER}; color: #33475B; }}
    table.mg-table td:last-child {{ text-align: right; color: {NAVY}; font-weight: 500; }}

    .mg-note {{ color: {STEEL}; font-size: 0.82rem; margin-top: 0.8rem; }}

    .mg-footer {{text-align: center; color: #052d66 ; font-size: 0.85rem; font-weight: 500; margin-top: 2.5rem;}}


    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong {{
        color: #052d66 !important;
        font-weight: 700 !important;
    }}

    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {{
        color: #8c8d8f !important;
        font-weight: 500 !important;
    }}



    @media (max-width: 640px) {{
        .mg-header {{ padding: 1rem; }}
        .mg-gauge {{ flex-basis: 100%; }}
    }}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 3. Helpers
# --------------------------------------------------

LOGO_SVG = f"""
<svg width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true">
  <g stroke="{TEAL}" stroke-width="3" stroke-linecap="round">
    <line x1="20" y1="2.5" x2="20" y2="8"/><line x1="20" y1="32" x2="20" y2="37.5"/>
    <line x1="2.5" y1="20" x2="8" y2="20"/><line x1="32" y1="20" x2="37.5" y2="20"/>
    <line x1="7.6" y1="7.6" x2="11.5" y2="11.5"/><line x1="28.5" y1="28.5" x2="32.4" y2="32.4"/>
    <line x1="32.4" y1="7.6" x2="28.5" y2="11.5"/><line x1="7.6" y1="32.4" x2="11.5" y2="28.5"/>
  </g>
  <circle cx="20" cy="20" r="11" stroke="{TEAL}" stroke-width="3"/>
  <path d="M14.5 20.5l4 4 7.5-8" stroke="#fff" stroke-width="2.6"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


@st.cache_data(ttl=10, show_spinner=False)
def check_backend():
    """Call the /health endpoint. Returns (info_dict | None)."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError):
        return None


def gauge_svg(score, threshold, failed):
    """Semicircular gauge showing the score, with a marker at the threshold."""
    score = min(max(score, 0.0), 1.0)
    threshold = min(max(threshold, 0.0), 1.0)
    color = RED if failed else GREEN

    def point(frac, radius):
        angle = math.pi * (1 - frac)
        return 100 + radius * math.cos(angle), 100 - radius * math.sin(angle)

    x1, y1 = point(threshold, 68)
    x2, y2 = point(threshold, 92)
    lx, ly = point(threshold, 104)

    return f"""
<svg viewBox="0 0 200 128" role="img"
     aria-label="Failure score {score * 100:.1f}% against a threshold of {threshold * 100:.0f}%">
  <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="#E3E9EF"
        stroke-width="14" stroke-linecap="butt"/>
  <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="{color}"
        stroke-width="14" pathLength="100"
        stroke-dasharray="{score * 100:.2f} 100"/>
  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"
        stroke="{NAVY}" stroke-width="2.5"/>
  <text x="{lx:.2f}" y="{ly:.2f}" font-size="8" fill="{NAVY}"
        text-anchor="middle" dominant-baseline="middle">{threshold * 100:.0f}%</text>
  <text x="100" y="92" font-size="26" font-weight="700" fill="{NAVY}"
        text-anchor="middle">{score * 100:.1f}%</text>
  <text x="100" y="110" font-size="8.5" fill="{STEEL}"
        text-anchor="middle">Failure score</text>
  <text x="20" y="118" font-size="7.5" fill="{STEEL}" text-anchor="middle">0%</text>
  <text x="180" y="118" font-size="7.5" fill="{STEEL}" text-anchor="middle">100%</text>
</svg>
"""


def friendly_api_error(response):
    """Turn an API error response into a short, readable message."""
    if response.status_code == 422:
        try:
            details = response.json().get("detail", [])
            lines = []
            for item in details:
                field = str(item.get("loc", ["input"])[-1]).replace("_", " ")
                lines.append(f"- **{field.capitalize()}**: {item.get('msg', 'invalid value')}")
            if lines:
                return "Some inputs were not accepted:\n\n" + "\n".join(lines)
        except (ValueError, AttributeError, TypeError):
            pass
        return "Some inputs were not accepted. Check the values and try again."
    if response.status_code >= 500:
        return (
            "The assessment service ran into a problem while processing "
            "this request. Try again in a moment."
        )
    return f"The service rejected the request (status {response.status_code})."


# --------------------------------------------------
# 4. Header with live backend status
# --------------------------------------------------


# --------------------------------------------------
# 4. Header with live backend status
# --------------------------------------------------

api_info = check_backend()

if api_info is not None:
    status_html = (
        '<span class="mg-pill">'
        '<span class="mg-dot on"></span>'
        'Backend connected'
        '</span>'
    )

    model_name = html.escape(str(api_info.get("model") or "Model"))
    model_version = html.escape(str(api_info.get("version") or "n/a"))

    model_html = (
        f'<span class="mg-pill">'
        f'{model_name} v{model_version}'
        f'</span>'
    )

else:
    status_html = (
        '<span class="mg-pill">'
        '<span class="mg-dot off"></span>'
        'Backend offline'
        '</span>'
    )

    model_html = (
        '<span class="mg-pill">'
        'Model version unavailable'
        '</span>'
    )


header_html = f"""
<div class="mg-header">
<div class="mg-brand">
{LOGO_SVG}
<div>
<h1>MachineGuard</h1>
<p>Intelligent Machine Failure Risk Assessment</p>
</div>
</div>
<div class="mg-meta">
{status_html}
{model_html}
</div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

if api_info is None:
    st.error(
        "The assessment service is not reachable. Start the MachineGuard "
        "API, then reload this page. You can still fill in the form, but "
        "an assessment cannot run until the service is back."
    )

# --------------------------------------------------
# 5. Input form
# --------------------------------------------------

st.markdown(
    '<div class="mg-panel-title">Machine operating parameters</div>'
    '<div class="mg-panel-sub">Enter the machine\'s current readings. '
    "Defaults show a typical operating state.</div>",
    unsafe_allow_html=True,
)

with st.form("machine_input_form"):
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="mg-group">Thermal and operational</div>', unsafe_allow_html=True)

        air_temperature = st.number_input(
            "Air temperature (K)",
            min_value=0.01,
            value=300.0,
            step=0.1,
            help="Temperature of the surrounding air in kelvin. Typical range is about 295 to 305 K.",
        )
        process_temperature = st.number_input(
            "Process temperature (K)",
            min_value=0.01,
            value=310.0,
            step=0.1,
            help="Temperature of the machining process in kelvin. Usually about 10 K above air temperature.",
        )
        rotational_speed = st.number_input(
            "Rotational speed (RPM)",
            min_value=0.01,
            value=1500.0,
            step=10.0,
            help="Spindle speed in revolutions per minute.",
        )

    with col2:
        st.markdown('<div class="mg-group">Mechanical</div>', unsafe_allow_html=True)

        torque = st.number_input(
            "Torque (Nm)",
            min_value=0.01,
            value=40.0,
            step=0.1,
            help="Rotational force applied by the machine, in newton-metres.",
        )
        tool_wear = st.number_input(
            "Tool wear (minutes)",
            min_value=0.0,
            value=100.0,
            step=1.0,
            help="Total time the current tool has been in use. Higher values mean a more worn tool.",
        )
        machine_type = st.selectbox(
            "Machine type",
            options=["L", "M", "H"],
            format_func=lambda x: {"L": "L - Low", "M": "M - Medium", "H": "H - High"}[x],
            help="Product quality variant processed by the machine: low, medium or high.",
        )

    submitted = st.form_submit_button(
        "Assess failure risk",
        type="primary",
        use_container_width=True,
    )


# --------------------------------------------------
# 6. Prediction and results
# --------------------------------------------------

if submitted:
    payload = {
        "air_temperature": air_temperature,
        "process_temperature": process_temperature,
        "rotational_speed": rotational_speed,
        "torque": torque,
        "tool_wear": tool_wear,
        "machine_type": machine_type,
    }

    response = None
    result = None

    with st.spinner("Analysing operating conditions..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.HTTPError:
            st.error(friendly_api_error(response))
        except requests.exceptions.Timeout:
            st.error("The assessment took too long to respond. Try again in a moment.")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not reach the assessment service. Make sure the "
                "MachineGuard API is running at the configured address."
            )
        except (requests.exceptions.RequestException, ValueError):
            st.error("Something went wrong while contacting the service. Please try again.")

    if result is not None:
        try:
            score = float(result["failure_score"])
            threshold = float(result["threshold"])
            failed = int(result["prediction"]) == 1
        except (KeyError, TypeError, ValueError):
            st.error("The service returned an unexpected response. Please contact the API maintainer.")
        else:
            tone = "fail" if failed else "ok"
            headline = "Failure risk detected" if failed else "No failure risk detected"
            explanation = (
                "The model classified these operating conditions as a potential "
                "machine failure. Consider an inspection before continuing."
                if failed
                else "The model did not classify these operating conditions as a "
                "failure risk."
            )

            st.markdown(
                f"""
<div class="mg-result {tone}">
  <div class="mg-result-grid">
    <div class="mg-gauge">{gauge_svg(score, threshold, failed)}</div>
    <div class="mg-verdict">
      <div class="mg-status {tone}">{headline}</div>
      <p>{explanation}</p>
      <div class="mg-stats">
        <div class="mg-stat"><span>Failure score</span><strong>{score * 100:.2f}%</strong></div>
        <div class="mg-stat"><span>Decision threshold</span><strong>{threshold * 100:.0f}%</strong></div>
        <div class="mg-stat"><span>Model prediction</span><strong>{"Failure risk" if failed else "No failure risk"}</strong></div>
      </div>
      <div class="mg-note">
        The prediction is made by comparing the score with the threshold: a score
        at or above it is flagged. The score is the model's estimated probability
        for the failure class. It is not calibrated, so it is not a guaranteed
        real-world failure probability.
      </div>
    </div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

            # Input summary
            st.markdown(
                '<div class="mg-panel-title" style="margin-top:1.5rem;">Submitted parameters</div>',
                unsafe_allow_html=True,
            )
            type_label = {"L": "L - Low", "M": "M - Medium", "H": "H - High"}[machine_type]
            rows = [
                ("Thermal and operational", None, None),
                ("Air temperature", f"{air_temperature:.1f}", "K"),
                ("Process temperature", f"{process_temperature:.1f}", "K"),
                ("Rotational speed", f"{rotational_speed:,.0f}", "RPM"),
                ("Mechanical", None, None),
                ("Torque", f"{torque:.1f}", "Nm"),
                ("Tool wear", f"{tool_wear:.0f}", "min"),
                ("Machine type", type_label, ""),
            ]
            body = ""
            for label, value, unit in rows:
                if value is None:
                    body += f'<tr><th colspan="2">{label}</th></tr>'
                else:
                    body += f"<tr><td>{label}</td><td>{value} {unit}</td></tr>"
            st.markdown(f'<table class="mg-table">{body}</table>', unsafe_allow_html=True)


# --------------------------------------------------
# 7. Model information
# --------------------------------------------------

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

with st.expander("About this model"):
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown("**Model:** Tuned Gradient Boosting")
        st.markdown("**Version:** 1.0.0")
        st.markdown("**Decision threshold:** 0.20")
    with info_col2:
        st.markdown("**Backend:** FastAPI")
        st.markdown("**Frontend:** Streamlit")
        st.markdown("**Dataset:** AI4I 2020 Predictive Maintenance")

st.markdown(
    '<div class="mg-footer">MachineGuard - Intelligent Machine Failure Risk Assessment</div>',
    unsafe_allow_html=True,
)