"""Generación de CSS completo para tema light/dark — solo estilos, sin JS."""

def generate_css(theme: str = "light") -> str:
    """Genera CSS inline con el tema activo."""

    if theme == "light":
        bg = "#FAFAFA"
        bg_card = "#FFFFFF"
        bg_hover = "#F3F2EF"
        text = "#1C1917"
        text2 = "#78716C"
        text3 = "#A8A29E"
        border = "#E7E5E4"
        border_lt = "#F0EFED"
        accent = "#D97757"
        accent_glow = "rgba(217,119,87,0.15)"
        success = "#10B981"
        err = "#EF4444"
        err_bg = "#FEF2F2"
        code_bg = "#1C1917"
        code_text = "#E7E5E4"
        skel = "#EDECE8"
        accent_soft = "#FDF2ED"
    else:
        bg = "#0C0A09"
        bg_card = "#1C1917"
        bg_hover = "#292524"
        text = "#E7E5E4"
        text2 = "#A8A29E"
        text3 = "#78716C"
        border = "#292524"
        border_lt = "#231F1E"
        accent = "#D97757"
        accent_glow = "rgba(217,119,87,0.25)"
        success = "#34D399"
        err = "#F87171"
        err_bg = "#450A0A"
        code_bg = "#0C0A09"
        code_text = "#E7E5E4"
        skel = "#292524"
        accent_soft = "#2D1A12"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400..700&display=swap');

:root {{
    --bg: {bg};
    --bg-card: {bg_card};
    --bg-hover: {bg_hover};
    --text: {text};
    --text2: {text2};
    --text3: {text3};
    --border: {border};
    --border-lt: {border_lt};
    --accent: {accent};
    --accent-glow: {accent_glow};
    --accent-soft: {accent_soft};
    --success: {success};
    --err: {err};
    --err-bg: {err_bg};
    --err-border: {err};
    --code-bg: {code_bg};
    --code-text: {code_text};
    --skel: {skel};
    --font: 'Inter', -apple-system, sans-serif;
    --mono: 'JetBrains Mono', 'Fira Code', monospace;
}}

.stApp, html, body {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 14px;
}}

.main > .block-container {{
    padding: 1rem 1.5rem !important;
    max-width: 1400px !important;
}}

/* ===== SIDEBAR ===== */
.sidebar-header {{
    padding: 12px 8px 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}}
.sidebar-logo-box {{
    background: var(--accent);
    color: white;
    width: 28px; height: 28px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 700;
}}
.sidebar-title {{
    font-weight: 600; font-size: 0.9rem; margin: 0;
}}
.sidebar-sub {{
    font-size: 0.65rem; color: var(--text3);
}}

.section-title {{
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text3);
    padding: 8px 4px;
    display: flex;
    align-items: center;
    gap: 5px;
}}

/* Schema tree */
.schema-col {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 2px 4px 2px 20px;
    font-size: 0.78rem;
    color: var(--text2);
    border-radius: 3px;
}}
.schema-type-badge {{
    font-family: var(--mono);
    font-size: 0.58rem;
    font-weight: 600;
    padding: 1px 5px;
    border-radius: 3px;
    letter-spacing: 0.02em;
    min-width: 32px;
    text-align: center;
}}
.type-int {{ background: #EFF6FF; color: #3B82F6; }}
.type-text {{ background: #F0FDF4; color: #16A34A; }}
.type-real {{ background: #FEFCE8; color: #CA8A04; }}
.type-date {{ background: #F3E8FF; color: #9333EA; }}

/* History */
.hist-item {{
    padding: 4px 4px;
    font-size: 0.78rem;
    border-left: 2px solid transparent;
    margin-bottom: 1px;
}}
.hist-q {{
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text);
}}
.hist-meta {{
    font-size: 0.6rem;
    color: var(--text3);
}}
.hist-badge {{
    font-size: 0.55rem; padding: 1px 5px; border-radius: 3px; font-weight: 600;
}}
.hist-ok {{ background: #ECFDF5; color: var(--success); }}
.hist-err {{ background: {err_bg}; color: var(--err); }}

/* ===== HERO ===== */
.hero-title {{
    text-align: center;
    font-size: 1.6rem;
    font-weight: 650;
    letter-spacing: -0.02em;
    margin-top: 8px;
    color: var(--text);
}}
.hero-sub {{
    text-align: center;
    font-size: 0.85rem;
    color: var(--text2);
    margin-bottom: 16px;
}}

/* Query area */
.query-wrap {{
    max-width: 600px;
    margin: 0 auto;
}}

/* Chips */
.chip-wrap {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    justify-content: center;
    max-width: 500px;
    margin: 8px auto 0;
}}
.chip-wrap .stButton button {{
    font-size: 0.72rem !important;
    padding: 2px 12px !important;
    border-radius: 20px !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text2) !important;
    white-space: nowrap;
    height: auto !important;
    min-height: 28px;
}}
.chip-wrap .stButton button:hover {{
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-soft) !important;
}}

/* ===== SQL CARD ===== */
.sql-card {{
    background: var(--code-bg);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
    overflow-x: auto;
}}
.sql-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}}
.sql-label {{
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #78716C;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 5px;
}}
.sql-time {{
    font-size: 0.6rem;
    color: #78716C;
    font-family: var(--mono);
}}
.sql-code {{
    font-family: var(--mono);
    font-size: 0.78rem;
    line-height: 1.6;
    color: var(--code-text);
    white-space: pre-wrap;
    word-break: break-word;
}}
.sql-keyword {{ color: #D97757; font-weight: 500; }}
.sql-function {{ color: #8B5CF6; font-weight: 500; }}
.sql-string {{ color: #34D399; }}
.sql-number {{ color: #60A5FA; }}
.sql-comment {{ color: #78716C; font-style: italic; }}

/* ===== DATA TABLE ===== */
.data-info {{
    display: flex;
    justify-content: space-between;
    padding: 6px 10px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    font-size: 0.72rem;
    color: var(--text2);
}}

/* ===== STATS ===== */
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 8px;
    margin-bottom: 12px;
}}
.stat-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
    text-align: center;
}}
.stat-label {{
    font-size: 0.55rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text3);
    font-weight: 600;
}}
.stat-value {{
    font-size: 1.1rem;
    font-weight: 650;
    color: var(--text);
    font-family: var(--mono);
}}

/* ===== RIGHT PANEL ===== */
.rp-section {{
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text3);
    margin: 12px 0 6px;
}}
.rp-card {{
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
    text-align: center;
    margin-bottom: 6px;
}}
.rp-label {{
    font-size: 0.55rem;
    text-transform: uppercase;
    color: var(--text3);
    font-weight: 600;
}}
.rp-value {{
    font-size: 1.3rem;
    font-weight: 650;
    font-family: var(--mono);
    color: var(--text);
}}
.rp-value-sm {{ font-size: 1rem; }}
.rp-mini {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-bottom: 6px; }}
.rp-mini-card {{
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 6px;
    text-align: center;
}}

/* ===== SKELETON ===== */
.skel {{
    background: linear-gradient(90deg, var(--skel) 25%, var(--border) 50%, var(--skel) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 5px;
}}
@keyframes shimmer {{
    0% {{ background-position: 200% 0; }}
    100% {{ background-position: -200% 0; }}
}}
.skel-line {{ height: 12px; margin-bottom: 8px; }}
.skel-block {{ height: 160px; margin-bottom: 8px; }}

/* ===== ERROR ===== */
.err-card {{
    background: var(--err-bg);
    border: 1px solid var(--err-border);
    border-radius: 6px;
    padding: 10px 14px;
    margin: 10px 0;
}}
.err-title {{
    font-weight: 600; color: var(--err); font-size: 0.8rem;
}}
.err-msg {{
    font-size: 0.78rem; color: var(--err); opacity: 0.9;
}}

/* ===== EMPTY ===== */
.empty-state {{
    text-align: center;
    padding: 24px 12px;
}}
.empty-title {{
    font-size: 0.85rem; font-weight: 500; color: var(--text);
}}
.empty-text {{
    font-size: 0.75rem; color: var(--text3); line-height: 1.5;
}}

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {{
    .main > .block-container {{
        padding: 0.5rem !important;
    }}
    .hero-title {{ font-size: 1.2rem; }}
    .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 640px) {{
    .chip-wrap {{ flex-wrap: nowrap; overflow-x: auto; justify-content: flex-start; }}
}}

/* ===== FOOTER ===== */
.app-footer {{
    text-align: center;
    padding: 24px 0 8px;
    border-top: 1px solid var(--border);
    margin-top: 24px;
    font-size: 0.6rem;
    color: var(--text3);
}}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

/* ===== TABS ===== */
div.row-widget.stButton > button[key*="tab_"] {{
    font-size: 0.78rem !important;
}}

/* ===== OVERRIDES ===== */
.stTextArea textarea {{
    font-family: var(--font) !important;
    font-size: 0.92rem !important;
    background: var(--bg-card) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
}}
.stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}}
.stButton button[kind="primary"] {{
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    font-family: var(--font) !important;
}}
.stButton button[kind="primary"]:hover {{
    background: #C96A4A !important;
    box-shadow: 0 2px 8px var(--accent-glow) !important;
}}
.stButton button[kind="secondary"] {{
    font-family: var(--font) !important;
    font-size: 0.8rem !important;
}}
[data-testid="stDataFrameResizable"] {{
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
}}
[data-testid="stDataFrameResizable"] thead tr th {{
    background: var(--bg-card) !important;
    border-bottom: 1px solid var(--border) !important;
}}
.stCheckbox label {{
    font-size: 0.82rem !important;
}}
.stTextInput input {{
    font-size: 0.78rem !important;
    background: var(--bg-card) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
    border-radius: 6px !important;
}}
.stTextInput input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}}
</style>
"""
