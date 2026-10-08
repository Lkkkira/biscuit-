"""Global CSS design system injection for professional vanilla white clinical SaaS UI aesthetics."""

import streamlit as st


def inject_custom_styles() -> None:
    """Inject tailored CSS for a sleek, modern clinical SaaS interface (Professional Vanilla White Theme)."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Overall Application Background & Base Typography (Vanilla White Theme) */
    .stApp {
        background-color: #FAF8F5 !important;
        color: #1C1917 !important;
    }

    /* Headings Styling */
    h1, h2, h3, h4, h5, h6 {
        color: #1C1917 !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }

    /* Main Container Spacing & Layout */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1380px;
    }

    /* Professional Vanilla Sidebar */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    div[data-testid="stSidebarUserContent"],
    div[data-testid="stSidebarContent"] {
        background-color: #F3EFEA !important;
        border-right: 1px solid #E6E2DA !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    section[data-testid="stSidebar"] label {
        color: #57534E !important;
    }

    section[data-testid="stSidebar"] h3 {
        color: #1C1917 !important;
    }

    /* Sidebar Navigation item hover & active states */
    [data-testid="stSidebarNav"] a {
        border-radius: 8px !important;
        padding: 0.45rem 0.75rem !important;
        margin: 0.15rem 0 !important;
        transition: all 0.2s ease !important;
        color: #44403C !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebarNav"] a:hover {
        background-color: #E7E3DA !important;
        color: #0F766E !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #0F766E !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(15, 118, 110, 0.25) !important;
    }

    /* User Profile Chip inside Sidebar */
    .user-profile-chip {
        background: #FFFFFF !important;
        border: 1px solid #E6E2DA !important;
        border-radius: 10px !important;
        padding: 0.85rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }

    .user-profile-name {
        font-weight: 600 !important;
        color: #1C1917 !important;
        font-size: 0.9rem !important;
    }

    .user-profile-email {
        font-size: 0.75rem !important;
        color: #78716C !important;
    }

    /* Professional Clinical Cards & Container Blocks */
    .pharma-card, div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background: #FFFFFF !important;
        border: 1px solid #E6E2DA !important;
        border-radius: 10px !important;
        padding: 1.25rem 1.35rem !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 1rem !important;
    }

    /* Metric KPI Card Component */
    .metric-container {
        background: #FFFFFF !important;
        border: 1px solid #E6E2DA !important;
        border-radius: 10px !important;
        padding: 1.15rem 1.25rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        border-top: 3px solid #0F766E !important;
        transition: all 0.2s ease !important;
    }

    .metric-container:hover {
        border-color: #D6D1C7 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
    }

    .metric-container.accent-amber { border-top-color: #D97706 !important; }
    .metric-container.accent-red { border-top-color: #DC2626 !important; }
    .metric-container.accent-blue { border-top-color: #2563EB !important; }
    .metric-container.accent-green { border-top-color: #059669 !important; }
    .metric-container.accent-teal { border-top-color: #0F766E !important; }
    .metric-container.accent-slate { border-top-color: #57534E !important; }
    .metric-container.accent-navy { border-top-color: #1C1917 !important; }

    .metric-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.35rem;
    }

    .metric-label {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: #78716C !important;
        text-transform: uppercase;
        letter-spacing: 0.04em !important;
    }

    .metric-value {
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        color: #1C1917 !important;
        line-height: 1.2 !important;
    }

    .metric-subtext {
        font-size: 0.8rem !important;
        color: #78716C !important;
        font-weight: 400 !important;
        margin-top: 0.25rem !important;
    }

    /* Clinical Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        white-space: nowrap;
    }

    .badge-safe {
        background-color: #F0FDF4 !important;
        color: #15803D !important;
        border: 1px solid #DCFCE7 !important;
    }

    .badge-warning {
        background-color: #FFFBEB !important;
        color: #B45309 !important;
        border: 1px solid #FDE68A !important;
    }

    .badge-critical {
        background-color: #FEF2F2 !important;
        color: #B91C1C !important;
        border: 1px solid #FEE2E2 !important;
    }

    .badge-info {
        background-color: #F0FDFA !important;
        color: #0F766E !important;
        border: 1px solid #CCFBF1 !important;
    }

    .badge-neutral {
        background-color: #F5F3EF !important;
        color: #57534E !important;
        border: 1px solid #E6E2DA !important;
    }

    /* Custom Form Control & Input Elements */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D6D1C7 !important;
        border-radius: 8px !important;
        color: #1C1917 !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #0F766E !important;
        box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15) !important;
    }

    /* Buttons Styling */
    div.stButton > button:first-child {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.45rem 1rem !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #0F766E !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(15, 118, 110, 0.2) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #115E59 !important;
        box-shadow: 0 4px 8px rgba(15, 118, 110, 0.3) !important;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D6D1C7 !important;
        color: #44403C !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background-color: #F5F3EF !important;
        border-color: #A8A29E !important;
        color: #1C1917 !important;
    }

    /* Tabs Component Styling */
    [data-baseweb="tab-list"] {
        background-color: transparent !important;
        gap: 0.25rem !important;
        border-bottom: 2px solid #E6E2DA !important;
    }

    [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0 !important;
        font-weight: 500 !important;
        color: #78716C !important;
        padding: 0.55rem 0.9rem !important;
    }

    [aria-selected="true"] {
        color: #0F766E !important;
        border-bottom: 2px solid #0F766E !important;
        font-weight: 600 !important;
        background-color: transparent !important;
    }

    /* Data Frame Clean Table */
    [data-testid="stDataFrame"] {
        border-radius: 8px !important;
        border: 1px solid #E6E2DA !important;
        overflow: hidden !important;
    }

    /* Clinical SaaS Header Banner */
    .pharma-header-banner {
        background: #FFFFFF !important;
        border: 1px solid #E6E2DA !important;
        border-radius: 10px !important;
        padding: 1.2rem 1.5rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
        margin-bottom: 1.25rem !important;
    }

    .pharma-header-banner h2 {
        margin: 0 !important;
        color: #1C1917 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }

    .pharma-header-banner p {
        margin: 0.25rem 0 0 0 !important;
        color: #78716C !important;
        font-size: 0.9rem !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
