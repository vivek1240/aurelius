"""
AURELIUS - AI-Powered Wealth Intelligence Platform
A sophisticated, premium interface for financial analysis using AI agents
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
import sys

# Add the finrobot module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from finrobot.utils import register_keys_from_json, get_current_date
from finrobot.data_source import FinnHubUtils, YFinanceUtils, FMPUtils

# Page configuration
st.set_page_config(
    page_title="AURELIUS | Wealth Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Classy UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    /* ========== ROOT VARIABLES ========== */
    :root {
        --bg-primary: #08080c;
        --bg-secondary: #0d0d12;
        --bg-tertiary: #121218;
        --bg-card: rgba(18, 18, 24, 0.85);
        --bg-card-hover: rgba(24, 24, 32, 0.95);
        --accent-gold: #d4af37;
        --accent-gold-light: #f4d03f;
        --accent-gold-dim: rgba(212, 175, 55, 0.15);
        --accent-emerald: #00c896;
        --accent-ruby: #ff4757;
        --text-primary: #f8f8f8;
        --text-secondary: #a0a0a8;
        --text-muted: #6b6b75;
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-accent: rgba(212, 175, 55, 0.25);
        --glass-blur: blur(20px);
        --shadow-elegant: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        --shadow-glow: 0 0 60px rgba(212, 175, 55, 0.08);
    }
    
    /* ========== GLOBAL STYLES ========== */
    .stApp {
        background: 
            radial-gradient(ellipse at 0% 0%, rgba(212, 175, 55, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 100% 100%, rgba(0, 200, 150, 0.02) 0%, transparent 50%),
            linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-primary) 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        padding: 3rem 2rem;
        max-width: 1400px;
    }
    
    /* ========== TYPOGRAPHY ========== */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    h4, h5, h6, p, span, div, label {
        font-family: 'DM Sans', sans-serif !important;
    }
    
    /* ========== HERO SECTION ========== */
    .hero-container {
        background: 
            linear-gradient(135deg, rgba(212, 175, 55, 0.05) 0%, rgba(0, 200, 150, 0.03) 100%),
            var(--bg-card);
        border: 1px solid var(--border-accent);
        border-radius: 28px;
        padding: 4rem;
        margin-bottom: 3rem;
        backdrop-filter: var(--glass-blur);
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-glow);
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
        opacity: 0.5;
    }
    
    .hero-container::after {
        content: '';
        position: absolute;
        top: -100px;
        right: -100px;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(212, 175, 55, 0.08) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(-20px, 20px) rotate(5deg); }
    }
    
    .hero-title {
        font-size: 4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--accent-gold-light) 0%, var(--accent-gold) 50%, #c9a227 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem;
        position: relative;
        z-index: 1;
        letter-spacing: -0.03em;
        text-shadow: 0 0 80px rgba(212, 175, 55, 0.3);
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary) !important;
        margin-bottom: 0;
        position: relative;
        z-index: 1;
        font-weight: 400;
        line-height: 1.7;
        max-width: 600px;
    }
    
    /* ========== METRIC CARDS ========== */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 20px;
        padding: 1.75rem;
        margin: 0.5rem 0;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        backdrop-filter: var(--glass-blur);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.03) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .metric-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-4px);
        box-shadow: var(--shadow-elegant), 0 0 40px rgba(212, 175, 55, 0.05);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-value {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--accent-emerald) !important;
        letter-spacing: -0.02em;
    }
    
    .metric-value.negative {
        color: var(--accent-ruby) !important;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* ========== FEATURE CARDS ========== */
    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 24px;
        padding: 2.25rem;
        margin: 1rem 0;
        transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.04) 0%, rgba(0, 200, 150, 0.02) 100%);
        opacity: 0;
        transition: opacity 0.5s ease;
    }
    
    .feature-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
        opacity: 0;
        transition: opacity 0.5s ease;
    }
    
    .feature-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-8px);
        box-shadow: var(--shadow-elegant);
    }
    
    .feature-card:hover::before,
    .feature-card:hover::after {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 2.75rem;
        margin-bottom: 1.25rem;
        display: block;
    }
    
    .feature-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.35rem;
        font-weight: 600;
        color: var(--text-primary) !important;
        margin-bottom: 0.75rem;
        letter-spacing: -0.01em;
    }
    
    .feature-desc {
        font-size: 0.95rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }
    
    /* ========== SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        border-right: 1px solid var(--border-subtle);
    }
    
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 200px;
        background: radial-gradient(ellipse at 50% 0%, rgba(212, 175, 55, 0.05) 0%, transparent 70%);
        pointer-events: none;
    }
    
    /* ========== INPUTS ========== */
    .stTextInput > div > div > input,
    .stTextArea textarea {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.95rem !important;
        padding: 0.85rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 3px var(--accent-gold-dim), 0 0 30px rgba(212, 175, 55, 0.1) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea textarea::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* ========== BUTTONS ========== */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-gold) 0%, #c9a227 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        color: #000 !important;
        font-weight: 700 !important;
        padding: 0.9rem 2.25rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.25) !important;
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(212, 175, 55, 0.35) !important;
        background: linear-gradient(135deg, var(--accent-gold-light) 0%, var(--accent-gold) 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 18px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 14px !important;
        color: var(--text-muted) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.25rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-secondary) !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-gold) 0%, #c9a227 100%) !important;
        color: #000 !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2) !important;
    }
    
    /* ========== DATAFRAMES ========== */
    .stDataFrame {
        border-radius: 18px !important;
        overflow: hidden !important;
        border: 1px solid var(--border-subtle) !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: var(--bg-card) !important;
    }
    
    /* ========== EXPANDERS ========== */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--border-accent) !important;
    }
    
    /* ========== CHART CONTAINER ========== */
    .chart-container {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
        position: relative;
    }
    
    .chart-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
        opacity: 0.3;
    }
    
    /* ========== STATUS BADGES ========== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'DM Sans', sans-serif;
        letter-spacing: 0.02em;
    }
    
    .status-positive {
        background: rgba(0, 200, 150, 0.12);
        color: var(--accent-emerald);
        border: 1px solid rgba(0, 200, 150, 0.25);
    }
    
    .status-negative {
        background: rgba(255, 71, 87, 0.12);
        color: var(--accent-ruby);
        border: 1px solid rgba(255, 71, 87, 0.25);
    }
    
    /* ========== SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--accent-gold) 0%, #c9a227 100%);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-gold-light);
    }
    
    /* ========== ANIMATIONS ========== */
    .loading-pulse {
        animation: loadingPulse 2s ease-in-out infinite;
    }
    
    @keyframes loadingPulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .shimmer {
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
    }
    
    /* ========== GRADIENT DIVIDER ========== */
    .gradient-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
        margin: 2.5rem 0;
        opacity: 0.4;
    }
    
    /* ========== RADIO BUTTONS ========== */
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stRadio label {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
        color: var(--text-secondary) !important;
    }
    
    .stRadio label:hover {
        border-color: var(--border-accent) !important;
        color: var(--text-primary) !important;
    }
    
    .stRadio label[data-checked="true"] {
        border-color: var(--accent-gold) !important;
        background: var(--accent-gold-dim) !important;
        color: var(--accent-gold) !important;
    }
    
    /* ========== SELECT BOXES ========== */
    .stSelectbox > div > div {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--border-accent) !important;
    }
    
    /* ========== PROGRESS BAR ========== */
    .stProgress > div > div {
        background: var(--bg-tertiary) !important;
        border-radius: 10px !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-gold) 0%, var(--accent-emerald) 100%) !important;
        border-radius: 10px !important;
    }
    
    /* ========== SUCCESS/ERROR/INFO BOXES ========== */
    .stSuccess {
        background: rgba(0, 200, 150, 0.1) !important;
        border: 1px solid rgba(0, 200, 150, 0.3) !important;
        border-radius: 14px !important;
        color: var(--accent-emerald) !important;
    }
    
    .stError {
        background: rgba(255, 71, 87, 0.1) !important;
        border: 1px solid rgba(255, 71, 87, 0.3) !important;
        border-radius: 14px !important;
    }
    
    .stInfo {
        background: rgba(212, 175, 55, 0.08) !important;
        border: 1px solid var(--border-accent) !important;
        border-radius: 14px !important;
    }
    
    /* ========== SPINNER ========== */
    .stSpinner > div {
        border-color: var(--accent-gold) transparent transparent transparent !important;
    }
    
    /* ========== METRICS (Streamlit native) ========== */
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        color: var(--accent-gold) !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API keys
@st.cache_resource
def init_api_keys():
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config_api_keys")
        if os.path.exists(config_path):
            register_keys_from_json(config_path)
            return True
    except Exception as e:
        st.warning(f"Could not load API keys: {e}")
    return False

# Initialize
api_keys_loaded = init_api_keys()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1.5rem 0;">
        <div style="
            width: 70px; 
            height: 70px; 
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem auto;
            font-size: 2rem;
        ">🏛️</div>
        <h2 style="
            margin: 0.5rem 0 0.25rem 0; 
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 1.75rem;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #f4d03f 0%, #d4af37 50%, #c9a227 100%); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent;
        ">AURELIUS</h2>
        <p style="color: #6b6b75; font-size: 0.8rem; font-family: 'DM Sans', sans-serif; letter-spacing: 0.05em; text-transform: uppercase;">Wealth Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Stock symbol input with label
    st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; font-weight: 600;'>Stock Symbol</p>", unsafe_allow_html=True)
    ticker = st.text_input("Stock Symbol", value="NVDA", placeholder="Enter ticker...", label_visibility="collapsed")
    
    st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 1rem 0 0.5rem 0; font-weight: 600;'>Date Range</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", datetime.now() - timedelta(days=365), label_visibility="collapsed")
    with col2:
        end_date = st.date_input("End", datetime.now(), label_visibility="collapsed")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Navigation with premium styling
    st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem; font-weight: 600;'>Navigation</p>", unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["🎛️ Command Deck", "🔬 Deep Scan", "🏛️ The Vault", "📡 Signal Wire", "🔮 The Oracle"],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Status with premium styling
    if api_keys_loaded:
        st.markdown("""
        <div style="
            background: rgba(0, 200, 150, 0.08);
            border: 1px solid rgba(0, 200, 150, 0.2);
            border-radius: 12px;
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        ">
            <span style="color: #00c896;">●</span>
            <span style="color: #00c896; font-size: 0.85rem; font-weight: 500;">API Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Configure API Keys")

# Main Content
if page == "🎛️ Command Deck":
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <div style="
                background: rgba(212, 175, 55, 0.15);
                border: 1px solid rgba(212, 175, 55, 0.3);
                border-radius: 8px;
                padding: 0.35rem 0.75rem;
                font-size: 0.7rem;
                color: #d4af37;
                font-weight: 600;
                letter-spacing: 0.1em;
                text-transform: uppercase;
            ">AI-Powered</div>
        </div>
        <h1 class="hero-title">Wisdom Meets<br/>Wealth</h1>
        <p class="hero-subtitle">Like the philosopher-emperor, AURELIUS combines timeless wisdom with cutting-edge AI to deliver institutional-grade analysis and strategic foresight.</p>
        <div style="display: flex; gap: 2rem; margin-top: 2rem; position: relative; z-index: 1;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #00c896;">◆</span>
                <span style="color: #a0a0a8; font-size: 0.85rem;">Real-time Data</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #d4af37;">◆</span>
                <span style="color: #a0a0a8; font-size: 0.85rem;">GPT-4 Analysis</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #00c896;">◆</span>
                <span style="color: #a0a0a8; font-size: 0.85rem;">Multi-Source Intel</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats for selected ticker
    if ticker:
        try:
            with st.spinner("Fetching market data..."):
                stock_data = YFinanceUtils.get_stock_data(
                    ticker,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                
                if not stock_data.empty:
                    current_price = stock_data['Close'].iloc[-1]
                    prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
                    price_change = ((current_price - prev_price) / prev_price) * 100
                    
                    high_52w = stock_data['High'].max()
                    low_52w = stock_data['Low'].min()
                    avg_volume = stock_data['Volume'].mean()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Current Price</div>
                            <div class="metric-value">${current_price:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        change_class = "" if price_change >= 0 else "negative"
                        sign = "+" if price_change >= 0 else ""
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Daily Change</div>
                            <div class="metric-value {change_class}">{sign}{price_change:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">52W Range</div>
                            <div class="metric-value" style="font-size: 1.3rem;">${low_52w:.0f} - ${high_52w:.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Avg Volume</div>
                            <div class="metric-value" style="font-size: 1.3rem;">{avg_volume/1e6:.1f}M</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Price Chart
                    st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 2rem 0 1rem 0; font-weight: 600;'>Price Movement</p>", unsafe_allow_html=True)
                    fig = go.Figure()
                    
                    fig.add_trace(go.Candlestick(
                        x=stock_data.index,
                        open=stock_data['Open'],
                        high=stock_data['High'],
                        low=stock_data['Low'],
                        close=stock_data['Close'],
                        name=ticker,
                        increasing_line_color='#00c896',
                        decreasing_line_color='#ff4757',
                        increasing_fillcolor='rgba(0, 200, 150, 0.3)',
                        decreasing_fillcolor='rgba(255, 71, 87, 0.3)'
                    ))
                    
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(12,12,18,0.95)',
                        font=dict(family="DM Sans", color="#a0a0a8", size=11),
                        xaxis=dict(
                            gridcolor='rgba(255,255,255,0.03)',
                            linecolor='rgba(255,255,255,0.06)',
                            rangeslider=dict(visible=False),
                            showgrid=True
                        ),
                        yaxis=dict(
                            gridcolor='rgba(255,255,255,0.03)',
                            linecolor='rgba(255,255,255,0.06)',
                            showgrid=True
                        ),
                        margin=dict(l=0, r=0, t=20, b=0),
                        height=420,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
    
    # Feature Cards
    st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 2rem 0 1.25rem 0; font-weight: 600;'>Platform Capabilities</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, rgba(0, 200, 150, 0.15) 0%, rgba(0, 200, 150, 0.05) 100%);
                border: 1px solid rgba(0, 200, 150, 0.25);
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1.25rem;
                font-size: 1.5rem;
            ">📊</div>
            <div class="feature-title">Deep Scan</div>
            <div class="feature-desc">Comprehensive technical analysis with moving averages, volume patterns, and momentum indicators.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
                border: 1px solid rgba(212, 175, 55, 0.25);
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1.25rem;
                font-size: 1.5rem;
            ">📑</div>
            <div class="feature-title">The Vault</div>
            <div class="feature-desc">Access the financial archives — income statements, balance sheets, and cash flow records.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, rgba(0, 200, 150, 0.15) 0%, rgba(212, 175, 55, 0.1) 100%);
                border: 1px solid rgba(212, 175, 55, 0.2);
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1.25rem;
                font-size: 1.5rem;
            ">🤖</div>
            <div class="feature-title">The Oracle</div>
            <div class="feature-desc">Consult our AI strategist for predictive insights, market forecasts, and investment guidance.</div>
        </div>
        """, unsafe_allow_html=True)

elif page == "🔬 Deep Scan":
    st.markdown("## 🔬 Deep Scan")
    st.markdown(f"### Asset Under Analysis: **{ticker}**")
    
    if st.button("🔄 Fetch Analysis", use_container_width=True):
        with st.spinner("Gathering stock data..."):
            try:
                # Get stock data
                stock_data = YFinanceUtils.get_stock_data(
                    ticker,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                
                if not stock_data.empty:
                    # Tabs for different views
                    tab1, tab2, tab3 = st.tabs(["📊 Price Chart", "📉 Technical", "📋 Data"])
                    
                    with tab1:
                        fig = go.Figure()
                        
                        # Candlestick
                        fig.add_trace(go.Candlestick(
                            x=stock_data.index,
                            open=stock_data['Open'],
                            high=stock_data['High'],
                            low=stock_data['Low'],
                            close=stock_data['Close'],
                            name='Price'
                        ))
                        
                        # Add moving averages
                        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
                        stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
                        
                        fig.add_trace(go.Scatter(
                            x=stock_data.index,
                            y=stock_data['MA20'],
                            name='MA20',
                            line=dict(color='#6366f1', width=2)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=stock_data.index,
                            y=stock_data['MA50'],
                            name='MA50',
                            line=dict(color='#a855f7', width=2)
                        ))
                        
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(20,20,35,0.8)',
                            font=dict(family="Space Grotesk"),
                            xaxis=dict(gridcolor='rgba(99,102,241,0.1)', rangeslider=dict(visible=False)),
                            yaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
                            height=500,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        # Volume chart
                        fig_vol = go.Figure()
                        colors = ['#10b981' if stock_data['Close'].iloc[i] >= stock_data['Open'].iloc[i] 
                                  else '#ef4444' for i in range(len(stock_data))]
                        
                        fig_vol.add_trace(go.Bar(
                            x=stock_data.index,
                            y=stock_data['Volume'],
                            marker_color=colors,
                            name='Volume'
                        ))
                        
                        fig_vol.update_layout(
                            title="Trading Volume",
                            template="plotly_dark",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(20,20,35,0.8)',
                            font=dict(family="Space Grotesk"),
                            height=300
                        )
                        
                        st.plotly_chart(fig_vol, use_container_width=True)
                        
                        # Stats
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 📊 Statistics")
                            stats = stock_data['Close'].describe()
                            st.dataframe(stats, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### 📈 Returns")
                            returns = stock_data['Close'].pct_change()
                            st.metric("Average Daily Return", f"{returns.mean()*100:.3f}%")
                            st.metric("Volatility (Std)", f"{returns.std()*100:.3f}%")
                            st.metric("Max Daily Gain", f"{returns.max()*100:.2f}%")
                            st.metric("Max Daily Loss", f"{returns.min()*100:.2f}%")
                    
                    with tab3:
                        st.dataframe(stock_data.tail(50), use_container_width=True)
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "🏛️ The Vault":
    st.markdown("## 🏛️ The Vault")
    st.markdown(f"### Financial Records: **{ticker}**")
    
    if st.button("📊 Load Financials", use_container_width=True):
        with st.spinner("Fetching financial data..."):
            try:
                tab1, tab2, tab3, tab4 = st.tabs(["📄 Income", "📊 Balance Sheet", "💵 Cash Flow", "📈 Metrics"])
                
                with tab1:
                    income = YFinanceUtils.get_income_stmt(ticker)
                    if income is not None and not income.empty:
                        st.markdown("### Income Statement")
                        # Format large numbers
                        income_display = income.copy()
                        st.dataframe(income_display, use_container_width=True)
                        
                        # Revenue chart
                        if 'Total Revenue' in income.index:
                            fig = px.bar(
                                x=income.columns.astype(str),
                                y=income.loc['Total Revenue'].values / 1e9,
                                title="Revenue (Billions)",
                                labels={'x': 'Period', 'y': 'Revenue ($B)'}
                            )
                            fig.update_layout(
                                template="plotly_dark",
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(20,20,35,0.8)'
                            )
                            fig.update_traces(marker_color='#6366f1')
                            st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    balance = YFinanceUtils.get_balance_sheet(ticker)
                    if balance is not None and not balance.empty:
                        st.markdown("### Balance Sheet")
                        st.dataframe(balance, use_container_width=True)
                
                with tab3:
                    cashflow = YFinanceUtils.get_cash_flow(ticker)
                    if cashflow is not None and not cashflow.empty:
                        st.markdown("### Cash Flow Statement")
                        st.dataframe(cashflow, use_container_width=True)
                
                with tab4:
                    try:
                        metrics = FMPUtils.get_financial_metrics(ticker, years=4)
                        if metrics is not None and not metrics.empty:
                            st.markdown("### Key Financial Metrics")
                            st.dataframe(metrics, use_container_width=True)
                            
                            # Visualize key metrics
                            if 'Revenue' in metrics.index:
                                col1, col2 = st.columns(2)
                                with col1:
                                    fig = px.line(
                                        x=metrics.columns,
                                        y=metrics.loc['Revenue'].values,
                                        title="Revenue Trend",
                                        markers=True
                                    )
                                    fig.update_layout(
                                        template="plotly_dark",
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(20,20,35,0.8)'
                                    )
                                    fig.update_traces(line_color='#6366f1')
                                    st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.info("Financial metrics require FMP API key")
                        
            except Exception as e:
                st.error(f"Error fetching financials: {str(e)}")

elif page == "📡 Signal Wire":
    st.markdown("## 📡 Signal Wire")
    st.markdown(f"### Intelligence Feed: **{ticker}**")
    
    if st.button("🔄 Fetch News", use_container_width=True):
        with st.spinner("Gathering market news..."):
            try:
                news_df = FinnHubUtils.get_company_news(
                    ticker,
                    (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d"),
                    max_news_num=10
                )
                
                if news_df is not None and not news_df.empty:
                    for _, row in news_df.iterrows():
                        with st.container():
                            st.markdown(f"""
                            <div class="feature-card">
                                <div class="feature-title">{row.get('headline', 'No headline')}</div>
                                <div class="feature-desc">{row.get('summary', 'No summary available')[:300]}...</div>
                                <div style="color: #6366f1; font-size: 0.8rem; margin-top: 0.5rem;">
                                    📅 {row.get('date', 'Unknown date')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No recent news found. Try a different date range.")
                    
            except Exception as e:
                st.error(f"Error fetching news: {str(e)}")
    
    # Company Profile
    st.markdown("### 🏢 Company Profile")
    if st.button("📋 Load Profile", use_container_width=True):
        with st.spinner("Loading company profile..."):
            try:
                profile = FinnHubUtils.get_company_profile(ticker)
                if profile:
                    st.markdown(f"""
                    <div class="feature-card">
                        <div class="feature-desc">{profile}</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading profile: {str(e)}")

elif page == "🔮 The Oracle":
    st.markdown("## 🔮 The Oracle")
    st.markdown("Consult with our AI-powered wealth strategist for predictive insights and investment guidance.")
    
    # Import OpenAI
    try:
        from openai import OpenAI
        
        # Load API key from config
        config_path = os.path.join(os.path.dirname(__file__), "OAI_CONFIG_LIST")
        openai_key = None
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                if config and len(config) > 0:
                    openai_key = config[0].get('api_key', '')
        
        openai_available = openai_key and not openai_key.startswith('<')
    except:
        openai_available = False
    
    # Agent selection
    agent_type = st.selectbox(
        "Select Agent Type",
        ["Market Forecaster", "Financial Analyst", "Report Writer"]
    )
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Chat interface
    user_query = st.text_area(
        "💬 Your Query",
        value=f"Analyze {ticker} stock and predict next week's price movement based on recent data and news.",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        run_agent = st.button("🚀 Run Analysis", use_container_width=True)
    
    if run_agent and user_query:
        if not openai_available:
            st.error("⚠️ OpenAI API key not configured. Please add your API key to OAI_CONFIG_LIST")
        else:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Gather Stock Data
                status_text.markdown("**📊 Step 1/4:** Fetching stock price data...")
                progress_bar.progress(10)
                
                stock_data = YFinanceUtils.get_stock_data(
                    ticker,
                    (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d")
                )
                
                if stock_data.empty:
                    st.error(f"Could not fetch stock data for {ticker}")
                else:
                    current_price = stock_data['Close'].iloc[-1]
                    price_change_1d = ((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]) / stock_data['Close'].iloc[-2]) * 100 if len(stock_data) > 1 else 0
                    price_change_1w = ((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-5]) / stock_data['Close'].iloc[-5]) * 100 if len(stock_data) > 5 else 0
                    price_change_1m = ((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]) * 100
                    high_30d = stock_data['High'].max()
                    low_30d = stock_data['Low'].min()
                    avg_volume = stock_data['Volume'].mean()
                    
                    stock_summary = f"""
Stock: {ticker}
Current Price: ${current_price:.2f}
1-Day Change: {price_change_1d:+.2f}%
1-Week Change: {price_change_1w:+.2f}%
1-Month Change: {price_change_1m:+.2f}%
30-Day High: ${high_30d:.2f}
30-Day Low: ${low_30d:.2f}
Avg Daily Volume: {avg_volume:,.0f}
"""
                    progress_bar.progress(25)
                    
                    # Step 2: Get Company Profile
                    status_text.markdown("**🏢 Step 2/4:** Fetching company profile...")
                    try:
                        company_profile = FinnHubUtils.get_company_profile(ticker)
                    except:
                        company_profile = f"Company: {ticker}"
                    progress_bar.progress(40)
                    
                    # Step 3: Get News
                    status_text.markdown("**📰 Step 3/4:** Gathering market news...")
                    try:
                        news_df = FinnHubUtils.get_company_news(
                            ticker,
                            (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                            datetime.now().strftime("%Y-%m-%d"),
                            max_news_num=5
                        )
                        if news_df is not None and not news_df.empty:
                            news_summary = "\n".join([
                                f"- {row.get('headline', 'No headline')}: {row.get('summary', '')[:200]}"
                                for _, row in news_df.iterrows()
                            ])
                        else:
                            news_summary = "No recent news available."
                    except:
                        news_summary = "News data unavailable."
                    progress_bar.progress(60)
                    
                    # Step 4: Get Basic Financials
                    status_text.markdown("**💰 Step 4/4:** Analyzing financials...")
                    try:
                        financials = FinnHubUtils.get_basic_financials(ticker)
                    except:
                        financials = "Financial data unavailable."
                    progress_bar.progress(75)
                    
                    # Build the prompt for AI analysis
                    analysis_prompt = f"""You are an expert financial analyst. Analyze the following data for {ticker} and provide:

1. **Current Market Position**: Brief assessment of current stock performance
2. **Key Positive Developments**: 2-3 bullish factors based on the data
3. **Potential Concerns**: 2-3 risk factors or bearish signals
4. **Technical Analysis**: Brief technical outlook based on price movements
5. **Next Week Prediction**: Predicted price movement (e.g., "up 2-3%" or "down 1-2%") with confidence level
6. **Summary**: A concise investment thesis

Here is the data:

=== STOCK PRICE DATA ===
{stock_summary}

=== COMPANY PROFILE ===
{company_profile}

=== RECENT NEWS ===
{news_summary}

=== FINANCIAL METRICS ===
{financials[:2000] if isinstance(financials, str) else str(financials)[:2000]}

User's specific query: {user_query}

Provide a comprehensive but concise analysis. Be specific with numbers and percentages. Format your response with clear sections using markdown headers."""

                    # Call OpenAI
                    status_text.markdown("**🤖 Generating AI Analysis...**")
                    progress_bar.progress(85)
                    
                    client = OpenAI(api_key=openai_key)
                    
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert financial analyst specializing in stock market analysis and predictions. Provide data-driven insights with specific numbers and clear reasoning."},
                            {"role": "user", "content": analysis_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1500
                    )
                    
                    ai_response = response.choices[0].message.content
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    # Display Results
                    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
                    
                    # Quick Stats
                    st.markdown("### 📊 Market Data Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Current Price</div>
                            <div class="metric-value">${current_price:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        change_class = "" if price_change_1w >= 0 else "negative"
                        sign = "+" if price_change_1w >= 0 else ""
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Weekly Change</div>
                            <div class="metric-value {change_class}">{sign}{price_change_1w:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        change_class = "" if price_change_1m >= 0 else "negative"
                        sign = "+" if price_change_1m >= 0 else ""
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Monthly Change</div>
                            <div class="metric-value {change_class}">{sign}{price_change_1m:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">30D Range</div>
                            <div class="metric-value" style="font-size: 1.2rem;">${low_30d:.0f}-${high_30d:.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # AI Analysis
                    st.markdown("### 🤖 AI Analysis Report")
                    st.markdown(f"""
                    <div class="feature-card" style="background: linear-gradient(145deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);">
                        <div style="color: #e0e0e0; line-height: 1.8;">
                            {ai_response.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Price Chart
                    st.markdown("### 📈 Price Movement (30 Days)")
                    fig = go.Figure()
                    
                    fig.add_trace(go.Candlestick(
                        x=stock_data.index,
                        open=stock_data['Open'],
                        high=stock_data['High'],
                        low=stock_data['Low'],
                        close=stock_data['Close'],
                        name=ticker,
                        increasing_line_color='#10b981',
                        decreasing_line_color='#ef4444'
                    ))
                    
                    # Add 10-day MA
                    stock_data['MA10'] = stock_data['Close'].rolling(window=10).mean()
                    fig.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['MA10'],
                        name='MA10',
                        line=dict(color='#6366f1', width=2)
                    ))
                    
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(20,20,35,0.8)',
                        font=dict(family="Space Grotesk", color="#e0e0e0"),
                        xaxis=dict(gridcolor='rgba(99,102,241,0.1)', rangeslider=dict(visible=False)),
                        yaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
                        margin=dict(l=0, r=0, t=30, b=0),
                        height=400,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Success message
                    st.success(f"✅ Analysis complete for {ticker}! Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("Make sure your OpenAI API key is valid and has sufficient credits.")

# Footer
st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem 1rem;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.75rem; margin-bottom: 0.75rem;">
        <div style="
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        ">🏛️</div>
        <span style="
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            color: #f8f8f8;
        ">AURELIUS</span>
    </div>
    <p style="color: #6b6b75; font-size: 0.8rem; margin: 0.5rem 0;">Wealth Intelligence Platform</p>
    <p style="color: #4a4a52; font-size: 0.7rem; margin: 0.25rem 0; font-style: italic;">"The object of life is not to be on the side of the majority, but to escape finding oneself in the ranks of the insane."</p>
    <div style="display: flex; align-items: center; justify-content: center; gap: 1.5rem; margin-top: 1rem;">
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">Deep Scan</span>
        <span style="color: #4a4a52;">•</span>
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">The Vault</span>
        <span style="color: #4a4a52;">•</span>
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">Signal Wire</span>
        <span style="color: #4a4a52;">•</span>
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">The Oracle</span>
    </div>
</div>
""", unsafe_allow_html=True)

