"""
Pixelle-Video Web UI - Custom Theme Styles

「晨空清新」清新淡雅主题配色方案
"""

# ─────────────────────────────────────────────────────────────
# 配色方案
# ─────────────────────────────────────────────────────────────
THEME = {
    "primary":        "#0EA5E9",   # 天蓝
    "primary_hover":  "#0284C7",   # 天蓝深
    "secondary":      "#38BDF8",   # 浅天蓝
    "cta":            "#FBBF24",   # 阳光黄
    "cta_hover":      "#F59E0B",   # 阳光黄深
    "background":     "#F0F9FF",   # 霜白蓝
    "card":           "#FFFFFF",   # 纯白
    "text":           "#0C4A6E",   # 深蓝灰
    "text_muted":     "#64748B",   # 中灰蓝
    "border":         "#BAE6FD",   # 浅蓝灰
    "hover_bg":       "#E0F2FE",   # 浅天蓝
    "shadow":         "rgba(0, 0, 0, 0.06)",
    "shadow_md":      "rgba(0, 0, 0, 0.08)",
    "danger":         "#EF4444",
    "warning":        "#F59E0B",
    "success":        "#22C55E",
    "info":           "#0EA5E9",
}

# ─────────────────────────────────────────────────────────────
# CSS 注入样式
# ─────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Global ─────────────────────────────────────────────── */
.stApp {
    background: """ + THEME["background"] + """;
    font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

/* ── Headings ───────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', sans-serif !important;
    color: """ + THEME["text"] + """ !important;
}

/* ── Hide default Streamlit decorations ─────────────────── */
#root > div:nth-child(1) > div > div > div > div > section > header {
    display: none;
}

/* ── Top Navigation Bar ─────────────────────────────────── */
.top-navbar {
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    padding: 0 32px;
    background: """ + THEME["card"] + """;
    border-bottom: 1px solid """ + THEME["border"] + """;
    box-shadow: 0 1px 3px """ + THEME["shadow"] + """;
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
    color: """ + THEME["text"] + """;
    text-decoration: none;
}

.nav-brand-icon {
    width: 28px;
    height: 28px;
    color: """ + THEME["primary"] + """;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 4px;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    color: """ + THEME["text_muted"] + """;
    text-decoration: none;
    transition: all 200ms ease-out;
    cursor: pointer;
    border: none;
    background: transparent;
}

.nav-link:hover {
    background: """ + THEME["hover_bg"] + """;
    color: """ + THEME["primary"] + """;
}

.nav-link.active {
    background: """ + THEME["hover_bg"] + """;
    color: """ + THEME["primary"] + """;
    font-weight: 600;
}

.nav-link svg {
    width: 18px;
    height: 18px;
}

/* ── Language Selector ──────────────────────────────────── */
.nav-lang-selector {
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid """ + THEME["border"] + """;
    background: """ + THEME["card"] + """;
    color: """ + THEME["text"] + """;
    font-size: 13px;
    cursor: pointer;
    transition: all 200ms ease-out;
}

.nav-lang-selector:hover {
    border-color: """ + THEME["primary"] + """;
}

/* ── Cards & Containers ─────────────────────────────────── */
.card {
    background: """ + THEME["card"] + """;
    border-radius: 12px;
    border: 1px solid """ + THEME["border"] + """;
    box-shadow: 0 2px 8px """ + THEME["shadow"] + """;
    padding: 20px;
    transition: box-shadow 200ms ease-out;
}

.card:hover {
    box-shadow: 0 4px 16px """ + THEME["shadow_md"] + """;
}

/* ── Buttons ────────────────────────────────────────────── */
button[kind="primary"], .stButton > button[data-baseweb="button"] {
    background: """ + THEME["primary"] + """ !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-family: 'Poppins', sans-serif !important;
    transition: all 200ms ease-out !important;
}

button[kind="primary"]:hover {
    background: """ + THEME["primary_hover"] + """ !important;
    box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3) !important;
}

/* ── CTA Buttons ────────────────────────────────────────── */
.cta-button {
    background: """ + THEME["cta"] + """ !important;
    color: """ + THEME["text"] + """ !important;
}

.cta-button:hover {
    background: """ + THEME["cta_hover"] + """ !important;
}

/* ── Inputs ─────────────────────────────────────────────── */
input, textarea, select {
    border-radius: 8px !important;
    border-color: """ + THEME["border"] + """ !important;
}

input:focus, textarea:focus, select:focus {
    border-color: """ + THEME["primary"] + """ !important;
    box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.15) !important;
}

/* ── Tabs ───────────────────────────────────────────────── */
button[data-baseweb="tab"] {
    color: """ + THEME["text_muted"] + """ !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 200ms ease-out !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: """ + THEME["primary"] + """ !important;
    background: """ + THEME["hover_bg"] + """ !important;
    font-weight: 600 !important;
}

/* ── Expander ───────────────────────────────────────────── */
.streamlit-expanderHeader {
    border-radius: 8px !important;
    transition: all 200ms ease-out !important;
}

.streamlit-expanderHeader:hover {
    background: """ + THEME["hover_bg"] + """ !important;
}

/* ── Content padding below sticky nav ───────────────────── */
.main-content {
    padding-top: 16px;
}

/* ── Streamlit container overrides ──────────────────────── */
[data-testid="stAppViewContainer"] > div {
    padding-top: 0 !important;
}

/* ── Hide Streamlit branding ────────────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 768px) {
    .top-navbar {
        padding: 0 12px;
        height: 56px;
    }
    .nav-link {
        padding: 6px 10px;
        font-size: 13px;
    }
    .nav-brand {
        font-size: 16px;
    }
}
</style>
"""
