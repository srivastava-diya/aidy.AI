"""Paper & ink UI theme for aidy.AI: design tokens, global CSS, and small HTML components for Streamlit."""

from html import escape
from typing import Optional

import streamlit as st

THEME = {
    "paper": "#F0ECE3",
    "sheet": "#FBF9F4",
    "ink": "#17140F",
    "ink_soft": "#5A5349",
    "ink_faint": "#938A7C",
    "rule": "#D7D0C1",
    "rule_strong": "#B3A894",
    "allowed": "#2C6144",
    "refused": "#A02B1E",
    "pending": "#8A6512",
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --paper: %(paper)s;
    --sheet: %(sheet)s;
    --ink: %(ink)s;
    --ink-soft: %(ink_soft)s;
    --ink-faint: %(ink_faint)s;
    --rule: %(rule)s;
    --rule-strong: %(rule_strong)s;
    --allowed: %(allowed)s;
    --refused: %(refused)s;
    --pending: %(pending)s;
    --bar-h: 62px;
    --serif: "Instrument Serif", "Iowan Old Style", Georgia, serif;
    --mono: "JetBrains Mono", ui-monospace, "SF Mono", Consolas, monospace;
    --sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
}

/* ---------- Canvas ---------- */
html, body, [data-testid="stApp"] {
    font-family: var(--sans);
    color: var(--ink);
    -webkit-font-smoothing: antialiased;
}
[data-testid="stApp"] {
    background-color: var(--paper);
    background-image:
        linear-gradient(rgba(23,20,15,.065) 1px, transparent 1px),
        linear-gradient(90deg, rgba(23,20,15,.065) 1px, transparent 1px),
        repeating-linear-gradient(0deg, rgba(23,20,15,.016) 0 1px, transparent 1px 3px);
    background-size: 24px 24px, 24px 24px, auto;
}
[data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"],
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"],
#MainMenu, footer { display: none !important; }
[data-testid="stAppViewContainer"] { overflow-x: hidden; }
.block-container { padding: calc(var(--bar-h) + 8px) clamp(16px, 3vw, 34px) 70px !important; max-width: 1180px; }

h1, h2, h3 {
    font-family: var(--serif) !important;
    font-weight: 400 !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em;
}
h4, h5 { font-family: var(--serif) !important; font-weight: 400 !important; font-size: 1.3rem !important; color: var(--ink) !important; }
p, li { color: var(--ink-soft); line-height: 1.62; font-size: 15px; }
strong, b { color: var(--ink); }
hr { border: 0 !important; border-top: 1px dotted var(--rule-strong) !important; margin: 2rem 0 !important; }
a { color: var(--ink) !important; text-decoration: none; border-bottom: 1px solid var(--rule-strong); }
a:hover { border-bottom-color: var(--ink); }
code { font-family: var(--mono) !important; background: transparent !important; color: var(--ink-soft) !important; font-size: 0.85em; }
pre { background: var(--sheet) !important; border: 1px solid var(--rule) !important; border-radius: 0 !important; }

/* ---------- Top bar ---------- */
.st-key-topbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 999990;
    background: var(--ink);
    height: var(--bar-h);
    padding: 0 max(clamp(16px, 3vw, 34px), calc(50vw - 590px));
}
.st-key-topbar [data-testid="stHorizontalBlock"] { align-items: stretch; gap: 22px; height: var(--bar-h); flex-wrap: nowrap; }
.st-key-topbar [data-testid="stColumn"] { display: flex; align-items: center; }
.st-key-topbar [data-testid="stColumn"] > div { width: 100%%; }
.st-key-topbar [data-testid="stElementContainer"] { margin: 0; }

.brand {
    font-family: var(--serif); font-size: 25px; letter-spacing: -0.01em;
    color: var(--paper); white-space: nowrap;
    padding-right: 26px; border-right: 1px solid rgba(240,236,227,.16);
    line-height: var(--bar-h);
}
.brand em { font-style: italic; opacity: .82; }

.st-key-topbar [role="radiogroup"] { flex-wrap: nowrap; gap: 0; overflow-x: auto; scrollbar-width: none; }
.st-key-topbar [data-testid="stRadioOption"] {
    margin: 0; padding: 0 13px; height: var(--bar-h);
    display: flex; align-items: center;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: background .15s, border-color .15s;
}
.st-key-topbar [data-testid="stRadioOption"] > div > div:not([data-testid="stMarkdownContainer"]) { display: none; }
.st-key-topbar [data-testid="stRadioOption"] p {
    font-family: var(--mono); font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase;
    color: rgba(240,236,227,.55); white-space: nowrap; margin: 0;
}
.st-key-topbar [data-testid="stRadioOption"]:hover { background: rgba(240,236,227,.05); }
.st-key-topbar [data-testid="stRadioOption"]:hover p { color: var(--paper); }
.st-key-topbar [data-testid="stRadioOption"][data-selected="true"] { border-bottom-color: var(--paper); }
.st-key-topbar [data-testid="stRadioOption"][data-selected="true"] p { color: var(--paper); }

.bar-status { display: flex; justify-content: flex-end; gap: 24px; font-family: var(--mono); white-space: nowrap; }
.bar-stat { display: flex; flex-direction: column; gap: 3px; font-size: 10.5px; letter-spacing: .06em; color: var(--paper); }
.bar-stat > span { font-size: 9px; letter-spacing: .16em; text-transform: uppercase; color: rgba(240,236,227,.5); }

/* ---------- Typography components ---------- */
.label {
    font-family: var(--mono); font-size: 11px; font-weight: 600;
    letter-spacing: .13em; text-transform: uppercase; color: var(--ink-soft);
}
.hero { padding: clamp(28px, 6vh, 64px) 0 clamp(22px, 4vh, 40px); border-bottom: 1px solid var(--ink); margin-bottom: 30px; }
.hero h1 {
    font-size: clamp(34px, 5vw, 58px) !important; line-height: 1.06 !important;
    margin: 12px 0 0 !important; padding: 0 !important;
}
.hero h1 em { font-style: italic; color: var(--ink-soft); }
.hero p { max-width: 60ch; margin: 16px 0 0; font-size: 15.5px; }

.section-head {
    display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
    margin: 38px 0 16px; padding-bottom: 9px; border-bottom: 1px solid var(--ink);
}

/* ---------- Surfaces ---------- */
.slip, .st-key-sheet {
    position: relative;
    background: var(--sheet);
    border: 1px solid var(--rule-strong);
    padding: 20px 24px 18px;
    margin-bottom: 18px;
    box-shadow: 0 10px 26px -20px rgba(23,20,15,.6);
}
.slip::before, .st-key-sheet::before {
    content: ""; position: absolute; inset: -1px -1px auto -1px; height: 6px;
    background: radial-gradient(circle at 4px 0, transparent 0 3.2px, var(--rule-strong) 3.4px 4px, transparent 4.2px) repeat-x;
    background-size: 8px 6px;
}
.st-key-sheet { padding: 28px 34px 26px; }
.slip h4 { margin: 0 0 8px; }
.slip p { margin: 0; font-size: 13.5px; }
.slip ul { margin: 0; padding-left: 1.1rem; font-size: 13.5px; }
.slip-head {
    display: flex; justify-content: space-between; align-items: center;
    min-height: 34px; border-bottom: 1px solid var(--ink); padding-bottom: 8px; margin-bottom: 4px;
}
.stage { display: grid; grid-template-columns: 108px 1fr; gap: 14px; padding: 12px 0; border-bottom: 1px dotted var(--rule); }
.stage:last-child { border-bottom: 0; }
.stage-value { font-size: 13.5px; color: var(--ink); }
.stage-value.serif { font-family: var(--serif); font-size: 19px; line-height: 1.35; }
.stage-value.mono { font-family: var(--mono); font-size: 12.5px; }
.stage-value.quote { font-style: italic; color: var(--ink-soft); }

.pillars { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-bottom: 1px dotted var(--rule); }
.pillar { padding: 26px 30px 28px 0; }
.pillar + .pillar { border-left: 1px dotted var(--rule); padding-left: 30px; }
.pillar h3 { font-size: 23px !important; line-height: 1.18; margin: 9px 0 10px !important; padding: 0 !important; }
.pillar p { margin: 0; font-size: 13.5px; }

.stamp {
    display: inline-block;
    font-family: var(--mono); font-weight: 700; font-size: 13px; letter-spacing: .16em;
    padding: 4px 10px; border: 2.5px solid currentColor;
    transform: rotate(-4deg); opacity: .85;
    animation: stamp-down .28s cubic-bezier(.2,1.6,.4,1) .12s both;
}
@keyframes stamp-down { from { opacity: 0; transform: rotate(-4deg) scale(1.7); } to { opacity: .85; transform: rotate(-4deg) scale(1); } }

.tag {
    display: inline-block; font-family: var(--mono); font-size: 11.5px; font-weight: 600; letter-spacing: .08em;
    text-transform: uppercase; padding: 5px 10px; border: 1.5px solid currentColor; color: var(--ink-soft);
    background: var(--sheet); box-shadow: 3px 3px 0 currentColor;
}
.tone-allowed { color: var(--allowed) !important; }
.tone-refused { color: var(--refused) !important; }
.tone-pending { color: var(--pending) !important; }
.tone-ink { color: var(--ink) !important; }

.ledger-wrap { overflow-x: auto; }
.ledger { width: 100%%; border-collapse: collapse; font-family: var(--mono); font-size: 11.5px; }
.ledger thead th {
    text-align: left; padding: 0 12px 7px 0; font-size: 10px; letter-spacing: .14em;
    text-transform: uppercase; color: var(--ink-faint); font-weight: 500; border-bottom: 1px solid var(--ink);
}
.ledger tbody td { padding: 9px 12px 9px 0; border-bottom: 1px solid var(--rule); vertical-align: top; color: var(--ink); }
.ledger tbody tr:hover td { background: rgba(23,20,15,.03); }
.ledger .num { font-variant-numeric: tabular-nums; text-align: right; padding-right: 22px; white-space: nowrap; }
.ledger .topic { font-family: var(--sans); font-size: 12.5px; color: var(--ink-soft); }

.empty-note { font-style: italic; color: var(--ink-faint); padding: 14px 0; }

/* ---------- Metrics ---------- */
[data-testid="stMetric"] { border-top: 1px solid var(--ink); padding-top: 10px; }
[data-testid="stMetricLabel"] p {
    font-family: var(--mono) !important; font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: .14em; text-transform: uppercase; color: var(--ink-soft) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--serif); font-size: 40px !important; line-height: 1.1;
    color: var(--ink) !important; font-variant-numeric: tabular-nums;
}

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
    font-family: var(--mono); font-size: 10.5px; letter-spacing: .16em; text-transform: uppercase;
    border-radius: 0; padding: 12px 20px; min-height: 0;
    background: transparent; color: var(--ink-soft);
    border: 1px solid var(--rule-strong);
    transition: background .14s, color .14s, border-color .14s;
}
.stButton > button p, .stDownloadButton > button p, [data-testid="stFormSubmitButton"] > button p { font-family: inherit; font-size: inherit; color: inherit; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--ink); color: var(--ink); background: transparent; }
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button {
    background: var(--ink); color: var(--sheet); border-color: var(--ink);
}
.stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button:hover {
    background: transparent; color: var(--ink); border-color: var(--ink);
}
.stButton > button:not([kind="primary"]):focus:not(:active) { border-color: var(--ink); color: var(--ink); }
.stButton > button[kind="primary"]:focus:not(:hover) { background: var(--ink); color: var(--sheet); }

/* ---------- Inputs ---------- */
[data-testid="stForm"] { background: transparent; border: 0; padding: 0; }
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"],
[data-testid="stSelectbox"] [role="group"], [data-testid="stNumberInputContainer"],
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
    background: #FFFDF8 !important;
    border: 1.5px solid var(--ink) !important;
    border-radius: 0 !important;
    transition: box-shadow .14s, transform .14s;
}
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stSelectbox"] [role="group"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within,
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
    box-shadow: 4px 4px 0 var(--ink) !important;
    transform: translate(-2px, -2px);
}
[data-testid="stTextInputRootElement"] input { font-family: var(--serif); font-size: 19px; color: var(--ink) !important; background: transparent !important; }
[data-testid="stTextAreaRootElement"] textarea { font-family: var(--sans); font-size: 15px; color: var(--ink) !important; background: transparent !important; }
[data-testid="stSelectbox"] input { font-family: var(--sans); font-size: 15px; color: var(--ink) !important; }
input::placeholder, textarea::placeholder { color: var(--ink-faint) !important; font-style: italic; }
[data-testid="stWidgetLabel"] p {
    font-family: var(--mono) !important; font-size: 11.5px !important; font-weight: 600 !important;
    letter-spacing: .12em; text-transform: uppercase; color: var(--ink) !important;
}
[data-testid="stTooltipIcon"] svg { color: var(--ink-soft); }
[data-testid="stSlider"] [role="slider"] { border-radius: 0 !important; background: var(--ink) !important; }

/* Numbered form boxes */
[class*="st-key-fbox"] {
    background: var(--sheet);
    border: 1.5px solid var(--ink);
    box-shadow: 6px 6px 0 var(--ink);
    padding: 0 26px 22px;
    margin-bottom: 26px;
}
.box-head {
    display: flex; align-items: center; gap: 14px;
    margin: 0 -26px 20px; padding: 12px 26px;
    border-bottom: 1.5px solid var(--ink);
    background: var(--paper);
}
.box-num {
    font-family: var(--mono); font-weight: 700; font-size: 13px;
    background: var(--ink); color: var(--paper); padding: 4px 8px; letter-spacing: .06em;
}
.box-sym { font-size: 18px; color: var(--ink); }
.box-title { font-family: var(--serif); font-size: 24px; color: var(--ink); line-height: 1; }
.box-sub { margin-left: auto; font-family: var(--sans); font-style: italic; font-size: 13.5px; color: var(--ink-soft); }

/* ---------- Tabs ---------- */
[data-testid="stTabs"] [role="tablist"] { gap: 0; border-bottom: 1px solid var(--ink); }
[data-testid="stTabs"] [role="tab"] { padding: 10px 18px !important; background: transparent !important; }
[data-testid="stTabs"] [role="tab"] p {
    font-family: var(--mono) !important; font-size: 10.5px !important; letter-spacing: .16em;
    text-transform: uppercase; color: var(--ink-faint);
}
[data-testid="stTabs"] [role="tab"]:hover p { color: var(--ink); }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] p { color: var(--ink); }
[data-baseweb="tab-highlight"] { background-color: var(--ink) !important; height: 2px !important; }
[data-baseweb="tab-border"] { display: none; }
[data-testid="stTabs"] [role="tabpanel"] { padding-top: 22px; }

/* ---------- Data, alerts, progress ---------- */
[data-testid="stDataFrame"] { border: 1px solid var(--rule-strong); }
[data-testid="stAlert"] > div {
    border-radius: 0 !important; border: 0 !important; border-left: 3px solid var(--pending) !important;
    background: rgba(138, 101, 18, .07) !important; color: var(--ink-soft) !important;
}
[data-testid="stProgress"] > div > div > div > div { background: var(--ink) !important; }
[data-testid="stCaptionContainer"] { font-family: var(--mono); font-size: 10.5px; letter-spacing: .04em; color: var(--ink-faint); }

@media (max-width: 760px) {
    .pillars { grid-template-columns: 1fr; }
    .pillar, .pillar + .pillar { padding: 22px 0; border-left: 0; border-bottom: 1px dotted var(--rule); }
    .stage { grid-template-columns: 1fr; gap: 5px; }
    .bar-status { display: none; }
    .brand { border-right: 0; line-height: 50px; font-size: 22px; }
    /* Stacked bar: brand row, then a horizontally scrollable nav row. */
    .st-key-topbar { height: auto; }
    .st-key-topbar [data-testid="stHorizontalBlock"] { height: auto; flex-wrap: wrap; gap: 0; }
    .st-key-topbar [data-testid="stColumn"] { width: 100%% !important; flex: 1 1 100%% !important; min-width: 0; }
    .st-key-topbar [data-testid="stColumn"]:first-child { height: 50px; flex-basis: 50px !important; }
    .st-key-topbar [data-testid="stColumn"]:last-child { display: none; }
    .st-key-topbar [data-testid="stRadioOption"] { height: 44px; padding: 0 11px; }
    .st-key-topbar [role="radiogroup"] { border-top: 1px solid rgba(240,236,227,.16); }
    .block-container { padding-top: 112px !important; }
    .box-sub { display: none; }
    [class*="st-key-fbox"] { padding: 0 16px 16px; box-shadow: 4px 4px 0 var(--ink); }
    .box-head { margin: 0 -16px 16px; padding: 10px 16px; }
}
</style>
"""

_TONES = {"success": "allowed", "error": "refused", "warning": "pending", "accent": "ink"}


def apply_theme():
    """Injects the global paper & ink stylesheet."""
    st.markdown(_CSS % THEME, unsafe_allow_html=True)


def _html(markup: str):
    # Collapse indentation so Markdown never mistakes nested HTML for a code block.
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def render_brand():
    """Serif wordmark for the top bar."""
    _html('<div class="brand">aidy<em>.AI</em></div>')


def render_bar_status(stats: list[tuple[str, str]]):
    """Small label/value pairs on the right of the top bar."""
    cells = "".join(f'<div class="bar-stat"><span>{escape(k)}</span>{escape(v)}</div>' for k, v in stats)
    _html(f'<div class="bar-status">{cells}</div>')


def box_head(number: str, symbol: str, title: str, subtitle: str = ""):
    """Header strip for a numbered form box: [01] ✦ Title ........ subtitle."""
    _html(
        f'<div class="box-head"><span class="box-num">{escape(number)}</span>'
        f'<span class="box-sym">{escape(symbol)}</span><span class="box-title">{escape(title)}</span>'
        f'<span class="box-sub">{escape(subtitle)}</span></div>'
    )


def page_header(title: str, subtitle: Optional[str] = None, eyebrow: Optional[str] = None, emphasis: Optional[str] = None):
    """Hero title with an optional italic `emphasis` suffix, mono eyebrow, and subtitle."""
    eyebrow_html = f'<div class="label">{escape(eyebrow)}</div>' if eyebrow else ""
    em_html = f" <em>{escape(emphasis)}</em>" if emphasis else ""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    _html(f'<div class="hero">{eyebrow_html}<h1>{escape(title)}{em_html}</h1>{subtitle_html}</div>')


def section_title(text: str, aside: str = ""):
    _html(f'<div class="section-head"><span class="label">{escape(text)}</span><span class="label">{escape(aside)}</span></div>')


def card(body: str, title: Optional[str] = None, icon: Optional[str] = None):
    """Receipt-style slip. `body` is trusted HTML; `title` and `icon` (a small label) are escaped."""
    icon_html = f'<div class="label">{escape(icon)}</div>' if icon else ""
    title_html = f"<h4>{escape(title)}</h4>" if title else ""
    _html(f'<div class="slip">{icon_html}{title_html}{body}</div>')


def pillars(items: list[tuple[str, str]]):
    """Numbered editorial columns: [(title, body), ...]."""
    cols = "".join(
        f'<div class="pillar"><div class="label">{i:02d}</div><h3>{escape(t)}</h3><p>{escape(b)}</p></div>'
        for i, (t, b) in enumerate(items, start=1)
    )
    _html(f'<div class="pillars">{cols}</div>')


def pill(text: str, tone: str = "neutral") -> str:
    """Returns HTML for a small bordered mono tag. tone: neutral | success | warning | error | accent."""
    tone_cls = f" tone-{_TONES[tone]}" if tone in _TONES else ""
    return f'<span class="tag{tone_cls}">{escape(text)}</span>'


def stamp(text: str, tone: str = "neutral") -> str:
    """Returns HTML for a rotated rubber-stamp verdict."""
    tone_cls = f" tone-{_TONES[tone]}" if tone in _TONES else ""
    return f'<span class="stamp{tone_cls}">{escape(text)}</span>'


def render_html(markup: str):
    """Renders trusted HTML markup (indentation-safe)."""
    _html(markup)
