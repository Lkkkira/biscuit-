"""Clinical SaaS KPI metric card component."""

from typing import Optional
import streamlit as st


def render_metric_card(
    title: str,
    value: str,
    subtext: Optional[str] = None,
    accent: str = "teal",  # "teal", "amber", "red", "blue", "green"
    icon: Optional[str] = None,
) -> None:
    """Render a clean clinical metric card with top accent border."""
    accent_class = f"accent-{accent}" if accent in ["amber", "red", "blue", "green", "teal"] else "accent-teal"

    subtext_html = f'<div class="metric-subtext">{subtext}</div>' if subtext else ""

    card_html = f"""
    <div class="metric-container {accent_class}">
        <div class="metric-header">
            <span class="metric-label">{title}</span>
        </div>
        <div class="metric-value">{value}</div>
        {subtext_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
