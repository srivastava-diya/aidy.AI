"""Settings and system configuration page."""

import streamlit as st
from aidy.core.config import settings
from aidy.ui.theme import page_header, section_title, card, pill


def mask_secret(secret: str | None) -> str:
    if not secret:
        return "Not configured"
    if len(secret) <= 8:
        return "****"
    return f"{secret[:3]}****{secret[-4:]}"


def render_settings_page():
    page_header("Settings", "Provider credentials, execution budgets, and environment setup.", eyebrow="System")

    section_title("Providers")
    providers = [
        ("OpenAI", "LLM", settings.OPENAI_API_KEY),
        ("SerpAPI", "Search", settings.SERPAPI_API_KEY),
        ("Tavily", "Search", settings.TAVILY_API_KEY),
    ]
    for col, (name, kind, key) in zip(st.columns(3), providers):
        with col:
            status = pill("Connected", "success") if key else pill("Not set", "neutral")
            card(
                f"<div class='kv'><span class='k'>{name}</span>{status}</div>"
                f"<p style='margin-top:0.6rem'>{kind} · <code>{mask_secret(key)}</code></p>"
            )

    section_title("Execution budgets")
    col1, col2 = st.columns(2)
    with col1:
        st.slider("HTTP request timeout (s)", min_value=5, max_value=60, value=settings.REQUEST_TIMEOUT_S)
        st.slider("Max search results per query", min_value=2, max_value=15, value=settings.MAX_SEARCH_RESULTS)
    with col2:
        st.number_input("Token budget per run", min_value=5000, max_value=100000, value=settings.MAX_TOKENS_PER_RUN, step=5000)
        st.selectbox("Default model", options=["gpt-4o-mini", "gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"])
    st.caption("These controls preview values for this session only. Persist changes in `.env`.")

    section_title("Environment")
    st.markdown("Create a `.env` file in the project root (see `.env.example`):")
    st.code(
        'SERPAPI_API_KEY="..."      # or TAVILY_API_KEY — enables live web search\n'
        'OPENAI_API_KEY="sk-..."    # optional LLM provider\n'
        'DATABASE_URL="sqlite:///data/aidy.db"',
        language="bash",
    )
    st.caption("With no keys set, aidy.AI runs in deterministic offline benchmark mode — fully functional, zero external cost.")
