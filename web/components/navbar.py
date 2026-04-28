"""
Pixelle-Video Web UI - Top Navigation Bar Component

Renders a custom top navigation bar with all menu items displayed at the top.
Uses st.button for navigation with custom CSS styling.
"""

import streamlit as st
from web.i18n import tr, get_available_languages, set_language
from web.components.theme import CUSTOM_CSS

# Navigation items definition
NAV_ITEMS = [
    {"page": "pages/1_🎬_Home.py", "icon": "🏠", "label": "首页"},
    {"page": "pages/2_📚_History.py", "icon": "📚", "label": "历史记录"},
]


def render_top_navbar():
    """
    Render the complete top navigation bar.
    Call this at the very top of every page, before any other content.
    """
    # Inject theme CSS once
    _inject_css()

    # Render interactive navbar
    _render_navbar()


def _inject_css():
    """Inject theme CSS on first render"""
    if "theme_css_injected" not in st.session_state:
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        st.session_state.theme_css_injected = True


def _render_navbar():
    """Render the navbar with Streamlit interactive controls"""
    current_page = st.session_state.get("current_page", "pages/1_🎬_Home.py")
    num_items = len(NAV_ITEMS)

    # Use st.columns for layout: brand | nav links | language
    brand_col, *nav_cols, lang_col, spacer_col = st.columns(
        [3] + [1] * num_items + [1, 2]
    )

    # Brand
    with brand_col:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;padding:8px 0;">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#0EA5E9" stroke-width="2">
                    <polygon points="23 7 16 12 23 17 23 7"></polygon>
                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                </svg>
                <span style="font-size:18px;font-weight:600;color:#0C4A6E;">Pixelle-Video</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Nav links
    for i, item in enumerate(NAV_ITEMS):
        with nav_cols[i]:
            is_active = item["page"] == current_page
            if st.button(
                f"{item['icon']} {item['label']}",
                key=f"nav_{item['page']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = item["page"]
                st.switch_page(item["page"])

    # Language selector
    with lang_col:
        languages = get_available_languages()
        lang_options = [f"{code} - {name}" for code, name in languages.items()]
        current_lang = st.session_state.get("language", "zh_CN")
        current_index = list(languages.keys()).index(current_lang) if current_lang in languages else 0

        selected = st.selectbox(
            "Language",
            options=lang_options,
            index=current_index,
            key="nav_lang",
            label_visibility="collapsed",
        )

        if selected:
            selected_code = selected.split(" - ")[0]
            if selected_code != st.session_state.get("language"):
                st.session_state.language = selected_code
                set_language(selected_code)
                st.rerun()

    # Spacer
    with spacer_col:
        pass

    # Divider line
    st.markdown(
        '<div style="border-top:1px solid #BAE6FD;margin:4px 0 12px 0;"></div>',
        unsafe_allow_html=True,
    )
