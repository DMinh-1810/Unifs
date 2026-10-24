"""Theme Sáng / Tối cho UniFs.

Toàn bộ màu nằm trong biến CSS (--bg, --text...) nên chỉ cần đổi bảng màu là
mọi thành phần (kể cả widget gốc của Streamlit: ô nhập, chat, expander, dropdown...)
đổi theo, không bị "nửa sáng nửa tối".
"""

LIGHT = {
    "bg": "#f6f8fc",
    "surface": "#ffffff",
    "surface2": "#eef3fa",
    "sidebar": "#ffffff",
    "border": "#dbe3ee",
    "text": "#0f172a",
    "muted": "#52617a",
    "primary": "#0057b8",
    "primary_hover": "#004a9e",
    "primary_text": "#ffffff",
    "user_bubble": "#e3efff",
    "bot_bubble": "#ffffff",
    "hover": "#f0f6ff",
    "shadow": "0 1px 3px rgba(15,23,42,.06), 0 6px 18px rgba(15,23,42,.05)",
    "wordmark_u": "#0057b8",
    "code_bg": "#eef3fa",
}

DARK = {
    "bg": "#0b1220",
    "surface": "#141d31",
    "surface2": "#1b2640",
    "sidebar": "#0f1729",
    "border": "#2a3857",
    "text": "#eef2fa",
    "muted": "#a9b6cc",
    "primary": "#3b8cff",
    "primary_hover": "#5a9fff",
    "primary_text": "#ffffff",
    "user_bubble": "#1c3260",
    "bot_bubble": "#141d31",
    "hover": "#1b2640",
    "shadow": "0 1px 3px rgba(0,0,0,.35), 0 8px 22px rgba(0,0,0,.28)",
    "wordmark_u": "#ffffff",
    "code_bg": "#0b1220",
}


def palette(dark: bool) -> dict:
    return DARK if dark else LIGHT


def build_css(dark: bool) -> str:
    c = palette(dark)
    vars_css = "\n".join(f"--{k.replace('_', '-')}: {v};" for k, v in c.items())
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

:root {{
{vars_css}
color-scheme: {'dark' if dark else 'light'};
}}

html, body, .stApp, button, input, textarea, select {{
    font-family: 'Be Vietnam Pro', 'Inter', 'Segoe UI', sans-serif !important;
}}

/* ---------- Nền & chữ ---------- */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background: var(--bg) !important;
    color: var(--text);
}}
[data-testid="stHeader"] {{ background: transparent !important; height: 0 !important; pointer-events: none !important; }}
[data-testid="stHeader"] * {{ pointer-events: auto; }}
[data-testid="stHeader"] [data-testid="stToolbar"] {{ pointer-events: none !important; }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDeployButton"] {{ display: none !important; }}
[data-testid="stBottom"], [data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"] {{
    background: var(--bg) !important;
}}
.block-container {{
    max-width: 920px !important;
    padding-top: 1rem !important;
    padding-bottom: 1.5rem !important;
}}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4, [data-testid="stMarkdownContainer"] strong,
label, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] {{
    color: var(--text);
}}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
    color: var(--muted) !important;
}}
[data-testid="stMarkdownContainer"] a {{ color: var(--primary); }}
hr {{ border-color: var(--border) !important; opacity: 1 !important; }}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label {{ color: var(--text); }}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] {{ color: var(--muted) !important; }}

/* ---------- Nút ---------- */
.stButton > button, [data-testid^="stBaseButton-secondary"] {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    font-weight: 600;
    min-height: 2.6rem;
    transition: background .15s, border-color .15s, transform .05s;
}}
.stButton > button p, [data-testid^="stBaseButton-secondary"] p {{ color: inherit !important; }}
.stButton > button:hover, [data-testid^="stBaseButton-secondary"]:hover {{
    background: var(--hover) !important;
    border-color: var(--primary) !important;
    color: var(--primary) !important;
}}
.stButton > button:active {{ transform: scale(.99); }}
.stButton > button[data-testid^="stBaseButton-primary"], .stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"],
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] {{
    background: var(--primary) !important;
    color: var(--primary-text) !important;
    border: 1px solid var(--primary) !important;
    border-radius: 12px !important;
    font-weight: 700;
    min-height: 2.8rem;
}}
button[data-testid^="stBaseButton-primary"] p {{ color: var(--primary-text) !important; }}
.stButton > button[kind="primary"]:hover, button[data-testid^="stBaseButton-primary"]:hover {{
    background: var(--primary-hover) !important;
    border-color: var(--primary-hover) !important;
    color: var(--primary-text) !important;
}}
[data-testid="stFormSubmitButton"] button {{
    border-radius: 12px !important;
    font-weight: 700;
    min-height: 2.8rem;
}}

/* ---------- Ô nhập, dropdown ---------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div,
[data-baseweb="textarea"], [data-baseweb="input"] > div {{
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: 12px !important;
}}
[data-baseweb="input"] input, [data-baseweb="base-input"] input,
[data-baseweb="select"] input, [data-baseweb="select"] div,
textarea {{
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}}
input::placeholder, textarea::placeholder {{
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
    opacity: .85;
}}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {{
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 25%, transparent) !important;
}}
[data-baseweb="popover"] > div, [data-baseweb="menu"], ul[role="listbox"] {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border);
    border-radius: 12px;
}}
li[role="option"] {{ color: var(--text) !important; background: transparent !important; }}
li[role="option"]:hover, li[aria-selected="true"] {{ background: var(--hover) !important; }}
[data-testid="stTooltipContent"] {{
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border);
}}
svg {{ fill: currentColor; }}

/* ---------- Form, expander ---------- */
[data-testid="stForm"] {{
    background: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 18px;
    padding: 1.2rem 1.2rem .6rem;
    box-shadow: var(--shadow);
}}
[data-testid="stExpander"] {{
    background: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 12px;
    overflow: hidden;
}}
[data-testid="stExpander"] summary {{ background: transparent !important; color: var(--text) !important; }}
[data-testid="stExpander"] summary:hover {{ background: var(--hover) !important; }}
[data-testid="stExpander"] summary p {{ font-weight: 600; color: var(--text) !important; }}
[data-testid="stExpander"] summary svg {{ color: var(--muted); }}
[data-testid="stAlert"] {{ border-radius: 12px; }}

/* ---------- Chat ---------- */
[data-testid="stChatMessage"] {{
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: .9rem 1.1rem;
    margin-bottom: .75rem;
    background: var(--bot-bubble) !important;
    box-shadow: var(--shadow);
}}
[data-testid="stChatMessage"]:not(:has([data-testid="stChatMessageAvatarImage"])) {{
    background: var(--user-bubble) !important;
    border-color: transparent;
    box-shadow: none;
}}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {{
    font-size: 1rem;
    line-height: 1.7;
    color: var(--text) !important;
}}
[data-testid="stChatMessage"] ul, [data-testid="stChatMessage"] ol {{ padding-left: 1.3rem; }}
[data-testid="stChatMessage"] li {{ margin: .15rem 0; }}
[data-testid="stChatMessage"] table {{ border-collapse: collapse; width: 100%; font-size: .93rem; }}
[data-testid="stChatMessage"] th, [data-testid="stChatMessage"] td {{
    border: 1px solid var(--border) !important;
    padding: .45rem .7rem !important;
    color: var(--text) !important;
    background: transparent !important;
}}
[data-testid="stChatMessage"] th {{ background: var(--surface2) !important; }}
code, pre {{ background: var(--code-bg) !important; color: var(--text) !important; border-radius: 8px; }}

[data-testid="stChatInput"], [data-testid="stChatInput"] > div {{
    background: var(--surface) !important;
    border-radius: 16px !important;
}}
[data-testid="stChatInput"] {{
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow);
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 25%, transparent) !important;
}}
[data-testid="stChatInput"] textarea {{ font-size: 1rem; }}
[data-testid="stChatInput"] *, [data-testid="stChatInput"] *:focus {{ outline: none !important; box-shadow: none !important; }}
[data-testid="stChatInput"] [data-baseweb], [data-testid="stChatInput"] > div, [data-testid="stChatInput"] > div > div {{ border-color: transparent !important; }}
[data-testid="stChatInputSubmitButton"] {{ color: var(--primary) !important; background: transparent !important; }}

/* ---------- Thương hiệu ---------- */
.fpt-brand {{ display:flex; align-items:center; gap:.65rem; font-weight:700; font-size:1.05rem; color:var(--text); }}
.fpt-boxes {{ display:inline-flex; gap:3px; }}
.fpt-box {{ padding:2px 7px; border-radius:4px; color:#fff !important; font-weight:800; font-size:.82rem; transform:skewX(-10deg); }}
.fpt-blue {{ background:#0066b2; }} .fpt-orange {{ background:#f37021; }} .fpt-green {{ background:#0db14b; }}
.unifs-wordmark {{ font-size:2.6rem; font-weight:800; letter-spacing:-.02em; line-height:1.1; margin:.2rem 0; }}
.unifs-wordmark .u-blue {{ color: var(--wordmark-u); }}
.unifs-wordmark .u-orange {{ color:#f37021; }}
.unifs-wordmark .u-green {{ color:#0db14b; }}
.unifs-wordmark .u-star {{ color: var(--wordmark-u); font-size:1.5rem; vertical-align:super; margin-left:2px; }}
.sb-brand-wrap {{ display:flex; align-items:center; gap:.75rem; padding:.2rem 0 .5rem; }}
.sb-avatar-circle {{ width:48px; height:48px; border-radius:50%; overflow:hidden; border:2px solid var(--primary); background:#fff; flex-shrink:0; }}
.sb-avatar-circle img {{ width:100%; height:100%; object-fit:cover; }}
.sb-wordmark {{ font-size:1.6rem; font-weight:800; line-height:1.05; }}
.sb-sub {{ font-size:.82rem; color:var(--muted); margin-bottom:1rem; line-height:1.4; }}
.sb-footer {{ margin-top:1.5rem; padding-top:.8rem; border-top:1px solid var(--border); font-size:.82rem; color:var(--muted); }}
.fpt-stripes {{ display:inline-flex; gap:4px; margin-bottom:6px; }}
.stripe {{ width:8px; height:18px; border-radius:2px; transform:skewX(-18deg); display:inline-block; }}

.hero-wrapper {{ text-align:center; margin:.4rem auto 1.3rem; max-width:620px; }}
.hero-mascot-img {{
    width:140px; height:140px; object-fit:contain; border-radius:50%;
    background:#fff; padding:6px; margin-bottom:.35rem;
    box-shadow: 0 8px 26px rgba(0,102,178,.28);
}}
.hero-subtitle {{ font-size:1.2rem; font-weight:700; color:var(--text); margin-bottom:.5rem; }}
.hero-greeting {{ font-size:1rem; color:var(--muted); line-height:1.65; }}
.hero-greeting b {{ color:var(--text); }}

.topbar-user {{ display:flex; align-items:center; justify-content:flex-end; gap:.55rem; padding-top:.3rem;
    font-size:.88rem; font-weight:600; color:var(--muted); }}
.topbar-avatar {{ width:34px; height:34px; border-radius:50%; background:var(--surface2); border:1px solid var(--border);
    display:flex; align-items:center; justify-content:center; font-size:1rem; }}
.ready-footer {{ text-align:center; font-size:.85rem; color:var(--muted); margin-top:.5rem; }}
.green-dot {{ display:inline-block; width:8px; height:8px; background:#10b981; border-radius:50%; margin-right:6px; }}

/* ---------- Nút chuyển Sáng/Tối ---------- */
[class*="st-key-theme_toggle"] button {{
    border-radius: 999px !important;
    min-height: 2.2rem;
    font-size: .85rem;
    padding: 0 .9rem;
    white-space: nowrap;
}}

/* ---------- 4 thẻ chủ đề (nút bấm được cả thẻ) ---------- */
[class*="st-key-cat_"] button {{
    width: 100%;
    min-height: 88px;
    height: auto;
    padding: .9rem 1.1rem;
    text-align: left;
    justify-content: flex-start;
    align-items: center;
    gap: .9rem;
    border-radius: 16px !important;
    box-shadow: var(--shadow);
    white-space: normal;
}}
[class*="st-key-cat_"] button > div {{ width:100%; justify-content:flex-start; text-align:left; display:flex; align-items:center; gap:.85rem; }}
[class*="st-key-cat_"] button [data-testid="stMarkdownContainer"] {{ display:block !important; flex:1; min-width:0; }}
[class*="st-key-cat_"] button [data-testid="stMarkdownContainer"] p {{ display:block !important; width:100%; }}
[class*="st-key-cat_"] button p:first-child {{ font-size: 1.02rem; font-weight: 700; margin:0; }}
[class*="st-key-cat_"] button p:not(:first-child) {{
    font-size: .86rem; font-weight: 400; margin:.2rem 0 0; color: var(--muted) !important;
}}
[class*="st-key-cat_"] button:hover p:not(:first-child) {{ color: var(--muted) !important; }}
[class*="st-key-cat_"] button [data-testid="stIconEmoji"], [class*="st-key-cat_"] button span[role="img"] {{
    font-size: 1.7rem;
}}

/* ---------- Câu hỏi gợi ý ---------- */
[class*="st-key-subq_"] button {{
    justify-content: flex-start; text-align: left; white-space: normal;
    padding: .7rem 1rem; font-weight: 500; line-height: 1.5;
}}
[class*="st-key-subq_"] button > div {{ justify-content:flex-start; text-align:left; }}
.subq-title {{ font-weight:700; font-size:1rem; margin:1.1rem 0 .5rem; color:var(--text); }}

/* ---------- Mobile ---------- */
@media (max-width: 640px) {{
    .unifs-wordmark {{ font-size:2.1rem; }}
    .hero-mascot-img {{ width:110px; height:110px; }}
    .block-container {{ padding-left:1rem !important; padding-right:1rem !important; }}
}}
</style>
"""
