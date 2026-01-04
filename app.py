"""
IKSHVAKU - AI-Powered Wealth Intelligence Platform
A sophisticated, premium interface for financial analysis using AI agents
Named after the legendary founder of the Solar Dynasty (Suryavansha)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
import sys

# Add the aurelius module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurelius.utils import register_keys_from_json, get_current_date
from aurelius.data_source import FinnHubUtils, YFinanceUtils, FMPUtils
from aurelius.functional.charting import MplFinanceUtils, ReportChartUtils, ComparisonCharts
from aurelius.functional.quantitative import BackTraderUtils
from aurelius.functional.comparison import StockComparator
import tempfile
import base64

# Page configuration
st.set_page_config(
    page_title="IKSHVAKU | Wealth Intelligence",
    page_icon="☀️",
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
    
    /* ========== TYPOGRAPHY - Scoped to custom classes ========== */
    .hero-title, .feature-title, .metric-label {
        font-family: 'Outfit', sans-serif !important;
    }
    
    .hero-subtitle, .feature-desc {
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
        pointer-events: none;
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
    }
    
    .metric-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-4px);
        box-shadow: var(--shadow-elegant), 0 0 40px rgba(212, 175, 55, 0.05);
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
    }
    
    .feature-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-8px);
        box-shadow: var(--shadow-elegant);
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
    
    /* ========== BUTTONS ========== */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-gold) 0%, #c9a227 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        color: #000 !important;
        font-weight: 700 !important;
        padding: 0.9rem 2.25rem !important;
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
    
    /* ========== CHART CONTAINER ========== */
    .chart-container {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    /* ========== STATUS BADGES ========== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
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
    
    /* ========== GRADIENT DIVIDER ========== */
    .gradient-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
        margin: 2.5rem 0;
        opacity: 0.4;
    }
    
    /* ========== METRICS (Streamlit native) ========== */
    [data-testid="stMetricValue"] {
        color: var(--accent-gold) !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API keys (supports Streamlit Cloud, Hugging Face Spaces, and local files)
@st.cache_resource
def init_api_keys():
    try:
        # Try environment variables first (for Hugging Face Spaces)
        if os.environ.get('FINNHUB_API_KEY') or os.environ.get('OPENAI_API_KEY'):
            return True
        
        # Try Streamlit secrets (for Streamlit Cloud)
        if hasattr(st, 'secrets'):
            try:
                if 'finnhub' in st.secrets and 'api_key' in st.secrets['finnhub']:
                    os.environ['FINNHUB_API_KEY'] = st.secrets['finnhub']['api_key']
                if 'fmp' in st.secrets and 'api_key' in st.secrets['fmp']:
                    os.environ['FMP_API_KEY'] = st.secrets['fmp']['api_key']
                if 'openai' in st.secrets and 'api_key' in st.secrets['openai']:
                    os.environ['OPENAI_API_KEY'] = st.secrets['openai']['api_key']
                if os.environ.get('FINNHUB_API_KEY'):
                    return True
            except:
                pass
        
        # Fall back to local config file
        config_path = os.path.join(os.path.dirname(__file__), "config_api_keys")
        if os.path.exists(config_path):
            register_keys_from_json(config_path)
            return True
    except Exception as e:
        st.warning(f"Could not load API keys: {e}")
    return False

# Get OpenAI API key (supports env vars, Streamlit secrets, and local file)
def get_openai_key():
    # Try environment variable first (for Hugging Face Spaces)
    if os.environ.get('OPENAI_API_KEY'):
        return os.environ.get('OPENAI_API_KEY')
    
    # Try Streamlit secrets
    if hasattr(st, 'secrets'):
        try:
            if 'openai' in st.secrets and 'api_key' in st.secrets['openai']:
                return st.secrets['openai']['api_key']
        except:
            pass
    
    # Fall back to local config file
    config_path = os.path.join(os.path.dirname(__file__), "OAI_CONFIG_LIST")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            if config and len(config) > 0:
                return config[0].get('api_key', '')
    return None

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
        ">☀️</div>
        <h2 style="
            margin: 0.5rem 0 0.25rem 0; 
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 1.75rem;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #f4d03f 0%, #d4af37 50%, #c9a227 100%); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent;
        ">IKSHVAKU</h2>
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
        ["🤖 AI Command Center", "🎛️ Command Deck", "🔬 Deep Scan", "🏛️ The Vault", "📈 Earnings Intel", "📊 Comparator", "📌 Watchlist", "🏦 Ownership", "💰 Valuation", "📊 Risk Lab", "📡 Signal Wire", "🔮 The Oracle", "⚔️ Backtest Arena", "📑 Report Forge", "📱 Social Pulse", "📚 Research Library"],
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
if page == "🤖 AI Command Center":
    st.title("🤖 AI Command Center")
    st.caption("Chat with AI to analyze stocks, create charts, run backtests, and more - all in one place.")
    
    st.divider()
    
    # Import tools
    from aurelius.functional.tools import TOOL_DEFINITIONS, ToolExecutor
    
    # Check OpenAI availability
    try:
        from openai import OpenAI
        openai_key = get_openai_key()
        openai_available = openai_key and not openai_key.startswith('<') and not openai_key.startswith('sk-your')
    except:
        openai_available = False
    
    if not openai_available:
        st.error("⚠️ OpenAI API key required. Configure in Streamlit secrets or OAI_CONFIG_LIST.")
        st.stop()
    
    # Initialize chat history
    if 'command_center_messages' not in st.session_state:
        st.session_state.command_center_messages = []
    
    # Available tools info box
    with st.expander("🛠️ Available AI Tools", expanded=False):
        st.markdown("""
        | Tool | Description | Example |
        |------|-------------|---------|
        | 📈 **Stock Data** | Get prices, income statements, balance sheets, cash flow | *"Show AAPL financials"* |
        | 📊 **Charts** | Candlestick, Line, Renko, Point & Figure charts | *"Create a chart for NVDA"* |
        | 📉 **Analysis** | Financial analysis, risk assessment, segment breakdown | *"Analyze TSLA risk"* |
        | ⚔️ **Backtest** | Test strategies: SMA, RSI, MACD, Bollinger Bands | *"Backtest RSI on MSFT"* |
        | 🏢 **Company Info** | Company profile, news, key metrics | *"Tell me about Apple"* |
        | 🆚 **Compare Stocks** | Compare multiple stocks side-by-side on financials, valuations & performance | *"Compare NVDA, AMD, INTC"* |
        | 📈 **Earnings Intel** | EPS history, beat rates, analyst estimates, next earnings | *"Show earnings for NVDA"* |
        | 🏦 **Ownership Intel** | Institutional holders, insider activity, ownership breakdown | *"Who owns NVDA?"* |
        | 📌 **Watchlist** | Add/remove stocks, view watchlist, save research notes | *"Add NVDA to watchlist"* |
        | 💰 **DCF Valuation** | Intrinsic value, WACC, terminal value, sensitivity analysis | *"Run DCF on AAPL"* |
        | 📊 **Risk Analysis** | VaR, Sharpe ratio, drawdown, volatility, beta, correlation | *"Risk analysis for NVDA"* |
        """)
    
    st.divider()
    
    # Display chat history
    for msg in st.session_state.command_center_messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                # Display any images for this message
                if msg.get("images"):
                    for img_data in msg["images"]:
                        st.image(f"data:image/png;base64,{img_data}", use_container_width=True)
    
    # Suggested prompts (only show if no messages yet)
    if not st.session_state.command_center_messages:
        st.markdown("**Try asking:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 Analyze NVDA", use_container_width=True):
                st.session_state.pending_prompt = "Analyze NVDA stock performance and key metrics"
                st.rerun()
        with col2:
            if st.button("📊 Chart AAPL", use_container_width=True):
                st.session_state.pending_prompt = "Create a candlestick chart for AAPL"
                st.rerun()
        with col3:
            if st.button("🆚 Compare Chips", use_container_width=True):
                st.session_state.pending_prompt = "Compare NVDA, AMD, and INTC on financials, valuations, and performance"
                st.rerun()
        
        col4, col5, col6 = st.columns(3)
        with col4:
            if st.button("⚔️ Backtest TSLA", use_container_width=True):
                st.session_state.pending_prompt = "Run RSI backtest on TSLA with $10,000"
                st.rerun()
        with col5:
            if st.button("💰 MSFT Financials", use_container_width=True):
                st.session_state.pending_prompt = "Show me Microsoft's income statement and key financials"
                st.rerun()
        with col6:
            if st.button("📈 NVDA Earnings", use_container_width=True):
                st.session_state.pending_prompt = "Show me NVDA earnings history, beat rate, and analyst estimates"
                st.rerun()
    
    # Additional quick actions row for new features
    st.markdown("**More Actions:**")
    col7, col8, col9 = st.columns(3)
    with col7:
        if st.button("🏦 AAPL Ownership", use_container_width=True):
            st.session_state.pending_prompt = "Who are the biggest owners of AAPL? Show me the ownership breakdown."
            st.rerun()
    with col8:
        if st.button("👥 NVDA Insiders", use_container_width=True):
            st.session_state.pending_prompt = "Show me insider trading activity for NVDA. Are insiders buying or selling?"
            st.rerun()
    with col9:
        if st.button("📋 My Watchlist", use_container_width=True):
            st.session_state.pending_prompt = "Show me my watchlist"
            st.rerun()
    
    # DCF quick actions
    col10, col11, col12 = st.columns(3)
    with col10:
        if st.button("💰 AAPL DCF", use_container_width=True):
            st.session_state.pending_prompt = "Run a DCF valuation for AAPL and show me the intrinsic value"
            st.rerun()
    with col11:
        if st.button("💰 NVDA DCF", use_container_width=True):
            st.session_state.pending_prompt = "What's the intrinsic value of NVDA based on DCF analysis?"
            st.rerun()
    with col12:
        if st.button("📊 MSFT Sensitivity", use_container_width=True):
            st.session_state.pending_prompt = "Show me sensitivity analysis for MSFT DCF valuation"
            st.rerun()
    
    # Risk quick actions
    col13, col14, col15 = st.columns(3)
    with col13:
        if st.button("📊 NVDA Risk", use_container_width=True):
            st.session_state.pending_prompt = "What's the risk profile of NVDA? Show me VaR, Sharpe ratio, and drawdown analysis."
            st.rerun()
    with col14:
        if st.button("📉 AAPL Drawdown", use_container_width=True):
            st.session_state.pending_prompt = "Show me drawdown analysis for AAPL"
            st.rerun()
    with col15:
        if st.button("🔗 Tech Correlation", use_container_width=True):
            st.session_state.pending_prompt = "Show correlation between NVDA, AMD, INTC, and SPY"
            st.rerun()
    
    # User input
    user_input = st.chat_input("Ask anything about stocks, charts, backtests, or analysis...")
    
    # Handle pending prompt from button click
    if 'pending_prompt' in st.session_state:
        user_input = st.session_state.pending_prompt
        del st.session_state.pending_prompt
    
    if user_input:
        # Add user message to history
        st.session_state.command_center_messages.append({"role": "user", "content": user_input})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Process AI response
        try:
            client = OpenAI(api_key=openai_key)
            
            # Build messages for API
            api_messages = [
                {
                    "role": "system",
                    "content": """You are IKSHVAKU, an expert AI financial analyst assistant named after the legendary founder of the Solar Dynasty. You have access to various tools to help users analyze stocks, create charts, run backtests, and get financial data.

When users ask about stocks or financial analysis:
1. Use the appropriate tools to get data
2. Provide clear, insightful analysis
3. Be specific with numbers and percentages
4. If creating charts, mention that a chart has been generated

Always be helpful, professional, and data-driven. Format responses clearly with sections if needed."""
                }
            ]
            
            # Add chat history (last 10 messages)
            for msg in st.session_state.command_center_messages[-10:]:
                api_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # First call: Check if tools are needed (non-streamed)
            with st.status("🔍 Analyzing your request...", expanded=True) as status:
                st.write("Determining the best approach...")
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=api_messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=2000
                )
                
                assistant_message = response.choices[0].message
                images = []
                
                # Check if tools were called
                if assistant_message.tool_calls:
                    tool_results = []
                    
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # Show which tool is being used
                        tool_display_names = {
                            "get_stock_data": "📈 Fetching stock data",
                            "create_stock_chart": "📊 Creating chart",
                            "get_income_statement": "💰 Getting income statement",
                            "get_balance_sheet": "📋 Getting balance sheet",
                            "get_cash_flow": "💵 Getting cash flow",
                            "get_company_profile": "🏢 Getting company profile",
                            "get_stock_news": "📰 Fetching news",
                            "run_backtest": "⚔️ Running backtest",
                            "compare_to_sp500": "📊 Comparing to S&P 500",
                            "get_risk_metrics": "📉 Calculating risk metrics",
                            "get_segment_analysis": "🔍 Analyzing segments"
                        }
                        st.write(tool_display_names.get(tool_name, f"🔧 Using {tool_name}..."))
                        
                        # Execute tool
                        result = ToolExecutor.execute(tool_name, tool_args)
                        
                        # Check for images
                        if result.get("has_image") and result.get("image_base64"):
                            images.append(result["image_base64"])
                            result_text = f"[Chart generated for {result.get('ticker', 'stock')}]"
                        else:
                            result_text = json.dumps(result, indent=2)
                        
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": result_text
                        })
                    
                    # Prepare messages for final response
                    api_messages.append(assistant_message)
                    for tr in tool_results:
                        api_messages.append(tr)
                    
                    status.update(label="✅ Data gathered! Generating response...", state="running")
                else:
                    status.update(label="✅ Ready!", state="complete")
            
            # Stream the final response
            with st.chat_message("assistant"):
                if assistant_message.tool_calls:
                    # Stream final response after tool execution
                    stream = client.chat.completions.create(
                        model="gpt-4o",
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=2000,
                        stream=True
                    )
                    
                    # Use st.write_stream for streaming display
                    response_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            response_placeholder.markdown(full_response + "▌")
                    
                    # Final render without cursor
                    response_placeholder.markdown(full_response)
                    ai_response = full_response
                    
                    # Display images after response
                    if images:
                        for img_data in images:
                            st.image(f"data:image/png;base64,{img_data}", use_container_width=True)
                else:
                    # Stream direct response (no tools)
                    stream = client.chat.completions.create(
                        model="gpt-4o",
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=2000,
                        stream=True
                    )
                    
                    response_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    ai_response = full_response
            
            # Add to session state for history
            st.session_state.command_center_messages.append({
                "role": "assistant", 
                "content": ai_response,
                "images": images if images else []
            })
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Clear chat button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.command_center_messages = []
            st.session_state.command_center_tool_results = {}
            st.rerun()

elif page == "🎛️ Command Deck":
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
        <p class="hero-subtitle">Named after the legendary founder of the Solar Dynasty, IKSHVAKU illuminates markets with ancient wisdom and cutting-edge AI to deliver institutional-grade analysis and strategic foresight.</p>
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
                    
                    # Stock vs S&P 500 Performance Comparison
                    st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 2rem 0 1rem 0; font-weight: 600;'>Performance vs S&P 500</p>", unsafe_allow_html=True)
                    
                    try:
                        # Get S&P 500 data for same period
                        sp500_data = YFinanceUtils.get_stock_data(
                            "^GSPC",
                            start_date.strftime("%Y-%m-%d"),
                            end_date.strftime("%Y-%m-%d")
                        )
                        
                        if not sp500_data.empty:
                            # Calculate percentage change from start
                            stock_pct = ((stock_data['Close'] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]) * 100
                            sp500_pct = ((sp500_data['Close'] - sp500_data['Close'].iloc[0]) / sp500_data['Close'].iloc[0]) * 100
                            
                            fig_compare = go.Figure()
                            
                            fig_compare.add_trace(go.Scatter(
                                x=stock_data.index,
                                y=stock_pct,
                                name=ticker,
                                line=dict(color='#d4af37', width=2.5),
                                fill='tozeroy',
                                fillcolor='rgba(212, 175, 55, 0.1)'
                            ))
                            
                            fig_compare.add_trace(go.Scatter(
                                x=sp500_data.index,
                                y=sp500_pct,
                                name='S&P 500',
                                line=dict(color='#6366f1', width=2, dash='dot')
                            ))
                            
                            fig_compare.update_layout(
                                template="plotly_dark",
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(12,12,18,0.95)',
                                font=dict(family="DM Sans", color="#a0a0a8", size=11),
                                xaxis=dict(gridcolor='rgba(255,255,255,0.03)', linecolor='rgba(255,255,255,0.06)'),
                                yaxis=dict(gridcolor='rgba(255,255,255,0.03)', linecolor='rgba(255,255,255,0.06)', title="Change %"),
                                margin=dict(l=0, r=0, t=20, b=0),
                                height=320,
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
                            
                            st.plotly_chart(fig_compare, use_container_width=True)
                            
                            # Show outperformance/underperformance
                            stock_total = stock_pct.iloc[-1]
                            sp500_total = sp500_pct.iloc[-1]
                            diff = stock_total - sp500_total
                            
                            if diff > 0:
                                st.markdown(f"""
                                <div style="background: rgba(0, 200, 150, 0.08); border: 1px solid rgba(0, 200, 150, 0.2); border-radius: 12px; padding: 1rem; text-align: center;">
                                    <span style="color: #00c896; font-weight: 600;">📈 {ticker} outperformed S&P 500 by {diff:.2f}%</span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style="background: rgba(255, 71, 87, 0.08); border: 1px solid rgba(255, 71, 87, 0.2); border-radius: 12px; padding: 1rem; text-align: center;">
                                    <span style="color: #ff4757; font-weight: 600;">📉 {ticker} underperformed S&P 500 by {abs(diff):.2f}%</span>
                                </div>
                                """, unsafe_allow_html=True)
                    except:
                        pass  # Silently skip if S&P data unavailable
                    
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
    
    # Chart options
    col1, col2, col3 = st.columns(3)
    with col1:
        chart_type = st.selectbox(
            "Chart Type",
            ["Candlestick", "Line", "OHLC", "Area", "Renko", "Point & Figure", "Hollow & Filled"],
            help="Select how to visualize price data. Renko/PnF are specialized chart types that filter noise."
        )
    with col2:
        show_ma = st.multiselect(
            "Moving Averages",
            [10, 20, 50, 100, 200],
            default=[20, 50],
            help="Select moving average periods to overlay"
        )
    with col3:
        show_volume = st.checkbox("Show Volume", value=True)
    
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
                        # Check if using specialized mplfinance chart types
                        mpl_chart_types = {"Renko": "renko", "Point & Figure": "pnf", "Hollow & Filled": "hollow_and_filled"}
                        
                        if chart_type in mpl_chart_types:
                            # Use mplfinance for specialized charts
                            st.info(f"📊 **{chart_type} Chart** - This chart type filters out minor price movements to show clearer trends.")
                            
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                                tmp_path = tmp.name
                            
                            try:
                                MplFinanceUtils.plot_stock_price_chart(
                                    ticker_symbol=ticker,
                                    start_date=start_date.strftime("%Y-%m-%d"),
                                    end_date=end_date.strftime("%Y-%m-%d"),
                                    save_path=tmp_path,
                                    type=mpl_chart_types[chart_type],
                                    style="nightclouds"  # Dark theme style
                                )
                                
                                # Display the generated image
                                st.image(tmp_path, use_container_width=True)
                                
                                # Cleanup
                                os.unlink(tmp_path)
                            except Exception as chart_err:
                                st.error(f"Error generating {chart_type} chart: {str(chart_err)}")
                        else:
                            # Use Plotly for standard chart types
                        fig = go.Figure()
                        
                            # Dynamic chart type
                            if chart_type == "Candlestick":
                        fig.add_trace(go.Candlestick(
                            x=stock_data.index,
                            open=stock_data['Open'],
                            high=stock_data['High'],
                            low=stock_data['Low'],
                            close=stock_data['Close'],
                                    name='Price',
                                    increasing_line_color='#00c896',
                                    decreasing_line_color='#ff4757'
                                ))
                            elif chart_type == "OHLC":
                                fig.add_trace(go.Ohlc(
                                    x=stock_data.index,
                                    open=stock_data['Open'],
                                    high=stock_data['High'],
                                    low=stock_data['Low'],
                                    close=stock_data['Close'],
                                    name='Price',
                                    increasing_line_color='#00c896',
                                    decreasing_line_color='#ff4757'
                                ))
                            elif chart_type == "Line":
                        fig.add_trace(go.Scatter(
                            x=stock_data.index,
                                    y=stock_data['Close'],
                                    name='Close Price',
                                    line=dict(color='#d4af37', width=2)
                                ))
                            elif chart_type == "Area":
                                fig.add_trace(go.Scatter(
                                    x=stock_data.index,
                                    y=stock_data['Close'],
                                    name='Close Price',
                                    fill='tozeroy',
                                    line=dict(color='#d4af37', width=2),
                                    fillcolor='rgba(212, 175, 55, 0.2)'
                                ))
                            
                            # Dynamic moving averages
                            ma_colors = ['#6366f1', '#a855f7', '#ec4899', '#f97316', '#22d3ee']
                            for i, ma_period in enumerate(show_ma):
                                ma_col = f'MA{ma_period}'
                                stock_data[ma_col] = stock_data['Close'].rolling(window=ma_period).mean()
                        fig.add_trace(go.Scatter(
                            x=stock_data.index,
                                    y=stock_data[ma_col],
                                    name=f'MA{ma_period}',
                                    line=dict(color=ma_colors[i % len(ma_colors)], width=1.5)
                        ))
                        
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(12,12,18,0.95)',
                                font=dict(family="DM Sans", color="#a0a0a8"),
                                xaxis=dict(gridcolor='rgba(255,255,255,0.03)', rangeslider=dict(visible=False)),
                                yaxis=dict(gridcolor='rgba(255,255,255,0.03)', title="Price ($)"),
                            height=500,
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        # Volume chart (conditional on checkbox)
                        if show_volume:
                        fig_vol = go.Figure()
                            colors = ['#00c896' if stock_data['Close'].iloc[i] >= stock_data['Open'].iloc[i] 
                                      else '#ff4757' for i in range(len(stock_data))]
                        
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
                                plot_bgcolor='rgba(12,12,18,0.95)',
                                font=dict(family="DM Sans", color="#a0a0a8"),
                                xaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
                                yaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
                            height=300
                        )
                        
                        st.plotly_chart(fig_vol, use_container_width=True)
                        else:
                            st.info("📊 Enable 'Show Volume' checkbox to view volume data")
                        
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
    
    # Import analyzer
    from aurelius.functional.analyzer import ReportAnalysisUtils
    
    if st.button("📊 Load Financials", use_container_width=True):
        with st.spinner("Fetching financial data..."):
            try:
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Income", "📊 Balance Sheet", "💵 Cash Flow", "📈 Metrics", "🔬 Deep Analysis"])
                
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
                    st.markdown("### 📈 PE & EPS Historical Performance")
                    
                    # Generate PE/EPS chart using our utility
                    try:
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                            pe_eps_path = tmp.name
                        
                        ReportChartUtils.get_pe_eps_performance(
                            ticker,
                            datetime.now().strftime("%Y-%m-%d"),
                            years=4,
                            save_path=pe_eps_path
                        )
                        
                        # Display the chart
                        with open(pe_eps_path, 'rb') as f:
                            pe_eps_data = base64.b64encode(f.read()).decode()
                        
                        st.markdown(f"""
                        <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 20px; padding: 1.5rem; margin-bottom: 1.5rem;">
                            <img src="data:image/png;base64,{pe_eps_data}" style="width: 100%; border-radius: 12px;">
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Clean up temp file
                        os.unlink(pe_eps_path)
                        
                    except Exception as e:
                        st.info(f"PE/EPS chart unavailable: {str(e)[:50]}")
                    
                    st.markdown("### 📊 Key Financial Metrics")
                    try:
                        metrics = FMPUtils.get_financial_metrics(ticker, years=4)
                        if metrics is not None and not metrics.empty:
                            st.dataframe(metrics, use_container_width=True)
                    except:
                        st.info("Financial metrics require FMP API key (paid tier)")
                
                with tab5:
                    st.markdown("### 🔬 AI-Powered Deep Analysis")
                    st.markdown("Generate comprehensive analysis of financial statements using AI.")
                    
                    analysis_type = st.selectbox(
                        "Select Analysis Type",
                        ["Income Statement Analysis", "Balance Sheet Analysis", "Cash Flow Analysis", "Risk Assessment", "Segment Analysis", "Business Highlights"]
                    )
                    
                    fiscal_year_analysis = st.selectbox(
                        "Fiscal Year",
                        ["2024", "2023", "2022", "2021"],
                        key="vault_fy"
                    )
                    
                    if st.button("🧠 Generate Analysis", use_container_width=True, key="deep_analysis_btn"):
                        with st.spinner("Generating AI analysis... This may take a moment."):
                            try:
                                # Create temp file for analysis
                                with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                                    tmp_path = tmp.name
                                
                                # Generate appropriate analysis
                                if analysis_type == "Income Statement Analysis":
                                    ReportAnalysisUtils.analyze_income_stmt(ticker, fiscal_year_analysis, tmp_path)
                                elif analysis_type == "Balance Sheet Analysis":
                                    ReportAnalysisUtils.analyze_balance_sheet(ticker, fiscal_year_analysis, tmp_path)
                                elif analysis_type == "Cash Flow Analysis":
                                    ReportAnalysisUtils.analyze_cash_flow(ticker, fiscal_year_analysis, tmp_path)
                                elif analysis_type == "Risk Assessment":
                                    ReportAnalysisUtils.get_risk_assessment(ticker, fiscal_year_analysis, tmp_path)
                                elif analysis_type == "Segment Analysis":
                                    ReportAnalysisUtils.analyze_segment_stmt(ticker, fiscal_year_analysis, tmp_path)
                                elif analysis_type == "Business Highlights":
                                    ReportAnalysisUtils.analyze_business_highlights(ticker, fiscal_year_analysis, tmp_path)
                                
                                # Read content
                                with open(tmp_path, 'r') as f:
                                    analysis_content = f.read()
                                os.unlink(tmp_path)
                                
                                # Use AI to summarize if OpenAI key available
                                openai_key = get_openai_key()
                                if openai_key and not openai_key.startswith('<') and len(openai_key) > 20:
                                    from openai import OpenAI
                                    client = OpenAI(api_key=openai_key)
                                    
                                    response = client.chat.completions.create(
                                        model="gpt-4o",
                                        messages=[
                                            {"role": "system", "content": f"You are an expert financial analyst. Analyze the following {analysis_type.lower()} data and provide a comprehensive analysis with key insights, trends, and recommendations. Format with clear sections using markdown."},
                                            {"role": "user", "content": analysis_content[:10000]}
                                        ],
                                        max_tokens=1000,
                                        temperature=0.7
                                    )
                                    
                                    ai_analysis = response.choices[0].message.content
                                    
                                    st.markdown(f"""
                                    <div class="feature-card" style="background: linear-gradient(145deg, rgba(0, 200, 150, 0.05) 0%, rgba(212, 175, 55, 0.05) 100%);">
                                        <div class="feature-title">🤖 AI Analysis: {analysis_type}</div>
                                        <div style="color: #e0e0e0; line-height: 1.8; margin-top: 1rem;">
                                            {ai_analysis.replace(chr(10), '<br>')}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                else:
                                    # Show raw data if no OpenAI key
                                    st.markdown("### 📋 Raw Analysis Data")
                                    st.info("Configure OpenAI API key for AI-powered summaries")
                                    with st.expander("View Raw Data", expanded=True):
                                        st.text(analysis_content[:3000])
                                
                                st.success(f"✅ {analysis_type} complete!")
                                
                            except Exception as e:
                                st.error(f"Analysis error: {str(e)[:100]}")
                                st.info("Some analyses require SEC API access. Check your API keys.")
                        
            except Exception as e:
                st.error(f"Error fetching financials: {str(e)}")

elif page == "📈 Earnings Intel":
    # Import earnings utilities
    from aurelius.functional.earnings import EarningsIntel
    from aurelius.functional.charting import EarningsCharts
    
    st.title("📈 Earnings Intelligence")
    st.caption("Track earnings history, analyst estimates, beat/miss streaks, and upcoming earnings dates.")
    
    st.divider()
    
    # Input section
    col1, col2 = st.columns([3, 1])
                                with col1:
        earnings_ticker = st.text_input("Stock Ticker", value="NVDA", placeholder="Enter ticker symbol").upper().strip()
    with col2:
        earnings_quarters = st.selectbox("Quarters History", [4, 6, 8, 12], index=2)
    
    if st.button("🔍 Analyze Earnings", use_container_width=True, type="primary"):
        if earnings_ticker:
            with st.spinner(f"Fetching earnings intelligence for {earnings_ticker}..."):
                try:
                    # Get all earnings data
                    earnings_history = EarningsIntel.get_earnings_history(earnings_ticker, earnings_quarters)
                    next_earnings = EarningsIntel.get_next_earnings(earnings_ticker)
                    analyst_data = EarningsIntel.get_analyst_estimates(earnings_ticker)
                    streak = EarningsIntel.get_earnings_surprise_streak(earnings_ticker)
                    revenue_data = EarningsIntel.get_revenue_history(earnings_ticker, earnings_quarters)
                    
                    # Quick Stats Row
                    st.markdown("### ⚡ Key Metrics")
                    summary = earnings_history.get("summary", {})
                    
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        beat_rate = summary.get("beat_rate", "N/A")
                        st.metric("Beat Rate", f"{beat_rate}%" if beat_rate != "N/A" else "N/A")
                    with m2:
                        streak_count = streak.get("current_streak", 0)
                        streak_type = streak.get("streak_type", "")
                        streak_emoji = "🔥" if streak_type == "beat" else "❄️" if streak_type == "miss" else ""
                        st.metric("Current Streak", f"{streak_emoji} {streak_count} {streak_type}s" if streak_count else "N/A")
                    with m3:
                        avg_surprise = summary.get("avg_surprise_pct", 0)
                        st.metric("Avg Surprise", f"{avg_surprise:+.2f}%" if avg_surprise else "N/A")
                    with m4:
                        days_until = next_earnings.get("days_until")
                        if days_until is not None:
                            st.metric("Next Earnings", f"In {days_until} days")
                        else:
                            st.metric("Next Earnings", "TBD")
                    
                    st.divider()
                    
                    # Tabs for different views
                    tab1, tab2, tab3, tab4 = st.tabs(["📊 EPS Analysis", "💰 Revenue Trends", "🎯 Analyst Targets", "📅 Next Earnings"])
                    
                    with tab1:
                        st.markdown("### EPS: Actual vs Estimate")
                        
                        # Generate EPS chart
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                            EarningsCharts.eps_surprise_chart(earnings_ticker, earnings_quarters, tmp.name)
                            st.image(tmp.name, use_container_width=True)
                        
                        # Earnings history table
                        if earnings_history.get("quarters"):
                            st.markdown("### 📋 Earnings History")
                            history_data = []
                            for q in earnings_history["quarters"]:
                                history_data.append({
                                    "Quarter": q["date"],
                                    "EPS Est": f"${q['eps_estimate']:.2f}" if q['eps_estimate'] else "N/A",
                                    "EPS Actual": f"${q['eps_actual']:.2f}" if q['eps_actual'] else "N/A",
                                    "Surprise": f"{q['surprise_pct']:+.1f}%" if q['surprise_pct'] else "N/A",
                                    "Result": "✅ Beat" if q.get('surprise_pct', 0) > 0 else "❌ Miss" if q.get('surprise_pct', 0) < 0 else "➖ Met"
                                })
                            st.dataframe(history_data, use_container_width=True, hide_index=True)
                    
                    with tab2:
                        st.markdown("### Revenue Trends")
                        
                        # Generate revenue chart
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                            EarningsCharts.revenue_trend_chart(earnings_ticker, earnings_quarters, tmp.name)
                            st.image(tmp.name, use_container_width=True)
                        
                        # Revenue summary
                        rev_summary = revenue_data.get("summary", {})
                        if rev_summary:
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                latest = rev_summary.get("latest_revenue")
                                if latest:
                                    st.metric("Latest Quarterly Revenue", f"${latest/1e9:.2f}B")
                            with c2:
                                avg_growth = rev_summary.get("avg_yoy_growth")
                                if avg_growth is not None:
                                    st.metric("Avg YoY Growth", f"{avg_growth:+.1f}%")
                            with c3:
                                trend = rev_summary.get("revenue_trend", "unknown")
                                trend_emoji = "📈" if trend == "growing" else "📉"
                                st.metric("Trend", f"{trend_emoji} {trend.title()}")
                    
                    with tab3:
                        st.markdown("### Analyst Price Targets")
                        
                        pt = analyst_data.get("price_targets", {})
                        if pt.get("current_price"):
                            # Generate analyst chart
                            import tempfile
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                                EarningsCharts.analyst_estimates_chart(earnings_ticker, tmp.name)
                                st.image(tmp.name, use_container_width=True)
                            
                            # Price target metrics
                            c1, c2, c3, c4 = st.columns(4)
                            with c1:
                                st.metric("Current Price", f"${pt.get('current_price', 0):.2f}")
                            with c2:
                                st.metric("Target Low", f"${pt.get('target_low', 0):.2f}")
                            with c3:
                                st.metric("Target Mean", f"${pt.get('target_mean', 0):.2f}")
                            with c4:
                                st.metric("Target High", f"${pt.get('target_high', 0):.2f}")
                            
                            upside = pt.get("upside_pct", 0)
                            if upside:
                                upside_color = "green" if upside > 0 else "red"
                                st.markdown(f"**Upside/Downside:** <span style='color: {upside_color}; font-size: 1.2em;'>{upside:+.1f}%</span>", unsafe_allow_html=True)
                        else:
                            st.info("Analyst price target data not available for this stock.")
                        
                        # EPS Estimates
                        eps_est = analyst_data.get("eps_estimates", {})
                        if eps_est:
                            st.markdown("### 📊 EPS Estimates by Period")
                            eps_rows = []
                            for period, data in eps_est.items():
                                eps_rows.append({
                                    "Period": period,
                                    "Low": f"${data.get('low', 0):.2f}" if data.get('low') else "N/A",
                                    "Avg": f"${data.get('avg', 0):.2f}" if data.get('avg') else "N/A",
                                    "High": f"${data.get('high', 0):.2f}" if data.get('high') else "N/A",
                                    "Analysts": data.get('num_analysts', 'N/A')
                                })
                            if eps_rows:
                                st.dataframe(eps_rows, use_container_width=True, hide_index=True)
                    
                    with tab4:
                        st.markdown("### 📅 Upcoming Earnings")
                        
                        if next_earnings.get("next_earnings_date"):
                            st.success(f"**Next Earnings Date:** {next_earnings['next_earnings_date']}")
                            
                            if next_earnings.get("days_until") is not None:
                                days = next_earnings["days_until"]
                                if days == 0:
                                    st.warning("⚠️ **Earnings are TODAY!**")
                                elif days <= 7:
                                    st.warning(f"⏰ **Earnings in {days} days** - Consider positioning before announcement")
                                else:
                                    st.info(f"📆 {days} days until next earnings report")
                            
                            # Estimates for upcoming
                            c1, c2 = st.columns(2)
                            with c1:
                                if next_earnings.get("eps_estimate"):
                                    st.metric("Expected EPS", f"${next_earnings['eps_estimate']:.2f}")
                            with c2:
                                if next_earnings.get("revenue_estimate"):
                                    st.metric("Expected Revenue", f"${next_earnings['revenue_estimate']/1e9:.2f}B")
                            
                            # Historical context
                            st.markdown("### 📈 Historical Context")
                            best = streak.get("best_surprise", {})
                            worst = streak.get("worst_surprise", {})
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if best:
                                    st.markdown(f"**Best Surprise:** {best.get('value', 0):+.1f}% ({best.get('date', 'N/A')})")
                            with c2:
                                if worst:
                                    st.markdown(f"**Worst Surprise:** {worst.get('value', 0):+.1f}% ({worst.get('date', 'N/A')})")
                        else:
                            st.info("Next earnings date not yet announced. Check back closer to earnings season.")
                    
                except Exception as e:
                    st.error(f"Error fetching earnings data: {str(e)}")
        else:
            st.warning("Please enter a ticker symbol.")
    
    # Tips section
    with st.expander("💡 Earnings Analysis Tips"):
        st.markdown("""
        **Understanding Earnings Metrics:**
        
        - **Beat Rate**: Percentage of quarters where actual EPS exceeded estimates
        - **Surprise %**: How much actual EPS deviated from analyst expectations
        - **Consecutive Beats**: Strong indicator of company execution and conservative guidance
        
        **Key Insights to Watch:**
        - Companies with high beat rates (>75%) tend to have conservative guidance
        - Large positive surprises can lead to price momentum
        - Revenue growth trends indicate business health
        - Analyst target spread shows consensus confidence
        
        **Trading Around Earnings:**
        - Stocks often move significantly on earnings day
        - Consider IV (implied volatility) before options trades
        - Historical surprise patterns can hint at guidance style
        """)

elif page == "📊 Comparator":
    st.title("📊 Stock Comparator")
    st.caption("Compare multiple stocks side-by-side on financials, valuations, growth, and performance.")
    
    st.divider()
    
    # Multi-stock input
    st.markdown("### Select Stocks to Compare")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        compare_input = st.text_input(
            "Enter ticker symbols separated by commas",
            value="NVDA, AMD, INTC",
            placeholder="e.g., NVDA, AMD, INTC, QCOM"
        )
    with col2:
        period_options = {"1 Month": 30, "3 Months": 90, "6 Months": 180, "1 Year": 365, "2 Years": 730}
        selected_period = st.selectbox("Period", list(period_options.keys()), index=3)
    
    # Parse tickers
    compare_tickers = [t.strip().upper() for t in compare_input.split(",") if t.strip()]
    
    if len(compare_tickers) < 2:
        st.warning("Please enter at least 2 ticker symbols to compare.")
    elif len(compare_tickers) > 5:
        st.warning("Maximum 5 stocks can be compared at once. Using first 5.")
        compare_tickers = compare_tickers[:5]
    
    if len(compare_tickers) >= 2 and st.button("🔍 Compare Stocks", use_container_width=True):
        with st.spinner(f"Comparing {', '.join(compare_tickers)}..."):
            try:
                # Get comparison data
                comparison_data = StockComparator.get_comparison_data(compare_tickers)
                performance_data = StockComparator.get_price_performance(compare_tickers, period_options[selected_period])
                best_in_class = StockComparator.identify_best_in_class(compare_tickers)
                comparison_table = StockComparator.create_comparison_table(compare_tickers)
                
                # Overview cards
                st.markdown("### 📋 Company Overview")
                overview_cols = st.columns(len(compare_tickers))
                for i, ticker in enumerate(compare_tickers):
                    with overview_cols[i]:
                        if ticker in comparison_data["overview"]:
                            info = comparison_data["overview"][ticker]
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3 style="color: #d4af37; margin-bottom: 0.5rem;">{ticker}</h3>
                                <p style="color: #f8f8f8; font-size: 1rem; margin-bottom: 0.5rem;">{info.get('name', ticker)}</p>
                                <p style="color: #a0a0a8; font-size: 0.85rem;">{info.get('sector', 'N/A')} • {info.get('industry', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.divider()
                
                # Tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Comparison Table", "📈 Performance", "💰 Margins", "🏆 Best in Class"])
                
                with tab1:
                    st.markdown("### Financial Comparison")
                    st.dataframe(comparison_table, use_container_width=True, height=500)
                    
                    # Download button
                    csv = comparison_table.to_csv()
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"comparison_{'_'.join(compare_tickers)}.csv",
                        mime="text/csv"
                    )
                
                with tab2:
                    st.markdown("### Price Performance")
                    
                    # Performance metrics
                    perf_cols = st.columns(len(compare_tickers) + 1)
                    all_tickers = compare_tickers + (["S&P 500"] if "S&P 500" in performance_data.get("performance", {}) else [])
                    
                    for i, t in enumerate(all_tickers):
                        with perf_cols[i] if i < len(perf_cols) else st.container():
                            if t in performance_data.get("performance", {}):
                                perf = performance_data["performance"][t]
                                return_val = perf.get("total_return", 0)
                                color = "#00c896" if return_val >= 0 else "#ff4757"
                                st.metric(
                                    t,
                                    f"{return_val:+.1f}%",
                                    f"Vol: {perf.get('volatility', 'N/A')}%" if 'volatility' in perf else None
                                )
                    
                    # Performance chart
                    st.markdown("#### Normalized Price Performance")
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        tmp_path = tmp.name
                    
                    ComparisonCharts.performance_comparison_chart(compare_tickers, period_options[selected_period], tmp_path)
                    st.image(tmp_path, use_container_width=True)
                    os.unlink(tmp_path)
                
                with tab3:
                    st.markdown("### Profit Margins Comparison")
                    
                    # Margins chart
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        tmp_path = tmp.name
                    
                    ComparisonCharts.margins_comparison_chart(compare_tickers, tmp_path)
                    st.image(tmp_path, use_container_width=True)
                    os.unlink(tmp_path)
                    
                    # Margins table
                    margins_data = []
                    for ticker in compare_tickers:
                        if ticker in comparison_data["financials"]:
                            fin = comparison_data["financials"][ticker]
                            margins_data.append({
                                "Ticker": ticker,
                                "Gross Margin": f"{fin.get('gross_margin', 0):.1f}%",
                                "Operating Margin": f"{fin.get('operating_margin', 0):.1f}%",
                                "Net Margin": f"{fin.get('net_margin', 0):.1f}%"
                            })
                    
                    if margins_data:
                        import pandas as pd
                        margins_df = pd.DataFrame(margins_data)
                        st.dataframe(margins_df, use_container_width=True, hide_index=True)
                
                with tab4:
                    st.markdown("### 🏆 Best in Class")
                    st.markdown("Which stock leads in each category:")
                    
                    if best_in_class:
                        best_cols = st.columns(3)
                        categories = list(best_in_class.items())
                        
                        for i, (category, winner) in enumerate(categories):
                            with best_cols[i % 3]:
                                st.markdown(f"""
                                <div class="metric-card" style="text-align: center;">
                                    <p style="color: #a0a0a8; font-size: 0.8rem; margin-bottom: 0.5rem;">{category}</p>
                                    <p style="color: #d4af37; font-size: 1.5rem; font-weight: bold;">{winner}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Could not determine best in class. Check if data is available for all stocks.")
                
            except Exception as e:
                st.error(f"Error comparing stocks: {str(e)}")
    
    # Quick comparison suggestions
    st.divider()
    st.markdown("### 💡 Quick Comparisons")
    
    suggestion_cols = st.columns(4)
    suggestions = [
        ("🖥️ Semiconductors", "NVDA, AMD, INTC, QCOM"),
        ("☁️ Cloud/Tech", "MSFT, GOOGL, AMZN, META"),
        ("🚗 EV/Auto", "TSLA, F, GM, RIVN"),
        ("💊 Pharma", "JNJ, PFE, MRK, ABBV")
    ]
    
    for i, (label, tickers) in enumerate(suggestions):
        with suggestion_cols[i]:
            if st.button(label, use_container_width=True, key=f"suggest_comp_{i}"):
                st.session_state.compare_suggestion = tickers
                st.rerun()
    
    # Handle suggestion click
    if 'compare_suggestion' in st.session_state:
        st.info(f"💡 Try comparing: {st.session_state.compare_suggestion}")
        del st.session_state.compare_suggestion

elif page == "📌 Watchlist":
    # Import storage utilities
    from aurelius.functional.storage import WatchlistManager, ResearchManager
    
    st.title("📌 Watchlist & Research")
    st.caption("Track your favorite stocks and save research notes for future reference.")
    
    st.divider()
    
    # Initialize managers
    watchlist_mgr = WatchlistManager()
    research_mgr = ResearchManager()
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 My Watchlist", "📝 Research Notes", "📊 Analysis History"])
    
    with tab1:
        st.markdown("### 📋 My Watchlist")
        
        # Add stock section
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            new_ticker = st.text_input("Add Stock", placeholder="Enter ticker symbol (e.g., NVDA)", key="add_watchlist_ticker").upper().strip()
        with col2:
            target_price = st.number_input("Target Price ($)", min_value=0.0, step=1.0, value=0.0, key="add_target_price")
        with col3:
            add_notes = st.text_input("Quick Note", placeholder="Optional note", key="add_quick_note")
        
        col_add, col_clear = st.columns(2)
        with col_add:
            if st.button("➕ Add to Watchlist", use_container_width=True, type="primary"):
                if new_ticker:
                    # Get current price
                    try:
                        stock_info = YFinanceUtils.get_stock_info(new_ticker)
                        current_price = stock_info.get("currentPrice") or stock_info.get("regularMarketPrice", 0)
                    except:
                        current_price = None
                    
                    result = watchlist_mgr.add_to_watchlist(
                        ticker=new_ticker,
                        added_price=current_price,
                        target_price=target_price if target_price > 0 else None,
                        notes=add_notes
                    )
                    
                    if result["success"]:
                        st.success(f"✅ Added {new_ticker} to watchlist!")
                        st.rerun()
                    else:
                        st.warning(result["message"])
                else:
                    st.warning("Please enter a ticker symbol")
        
        st.divider()
        
        # Display watchlist
        watchlist_items = watchlist_mgr.get_watchlist_items()
        
        if watchlist_items:
            st.markdown(f"**{len(watchlist_items)} stocks in your watchlist**")
            
            # Create data with current prices
            watchlist_data = []
            for item in watchlist_items:
                ticker_sym = item["ticker"]
                try:
                    stock_info = YFinanceUtils.get_stock_info(ticker_sym)
                    current_price = stock_info.get("currentPrice") or stock_info.get("regularMarketPrice", 0)
                    
                    added_price = item.get("added_price", 0) or 0
                    change_pct = ((current_price - added_price) / added_price * 100) if added_price else 0
                    
                    # Target progress
                    target = item.get("target_price")
                    if target and added_price:
                        target_progress = ((current_price - added_price) / (target - added_price) * 100) if target != added_price else 100
                    else:
                        target_progress = None
                    
                    watchlist_data.append({
                        "Ticker": ticker_sym,
                        "Current": f"${current_price:.2f}",
                        "Added At": f"${added_price:.2f}" if added_price else "N/A",
                        "Change": f"{change_pct:+.2f}%" if added_price else "N/A",
                        "Target": f"${target:.2f}" if target else "—",
                        "Notes": item.get("notes", "")[:30] + "..." if item.get("notes") and len(item.get("notes", "")) > 30 else item.get("notes", "—"),
                        "Added Date": item.get("added_at", "")[:10] if item.get("added_at") else "N/A"
                    })
            except Exception as e:
                    watchlist_data.append({
                        "Ticker": ticker_sym,
                        "Current": "Error",
                        "Added At": str(item.get("added_price", "N/A")),
                        "Change": "—",
                        "Target": str(item.get("target_price", "—")),
                        "Notes": item.get("notes", "—"),
                        "Added Date": item.get("added_at", "N/A")[:10] if item.get("added_at") else "N/A"
                    })
            
            # Display as dataframe
            import pandas as pd
            df = pd.DataFrame(watchlist_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Remove stock section
            st.markdown("---")
            col_remove, col_space = st.columns([1, 2])
            with col_remove:
                remove_ticker = st.selectbox(
                    "Remove Stock",
                    options=[""] + [item["ticker"] for item in watchlist_items],
                    key="remove_ticker_select"
                )
                if remove_ticker and st.button("🗑️ Remove", use_container_width=True):
                    result = watchlist_mgr.remove_from_watchlist(remove_ticker)
                    if result["success"]:
                        st.success(f"Removed {remove_ticker}")
                        st.rerun()
        else:
            st.info("📌 Your watchlist is empty. Add stocks above to start tracking!")
            
            # Quick add suggestions
            st.markdown("**Quick Add Popular Stocks:**")
            quick_add_cols = st.columns(5)
            popular_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "TSLA"]
            for i, t in enumerate(popular_tickers):
                with quick_add_cols[i]:
                    if st.button(t, key=f"quick_add_{t}", use_container_width=True):
                        try:
                            stock_info = YFinanceUtils.get_stock_info(t)
                            current_price = stock_info.get("currentPrice") or stock_info.get("regularMarketPrice", 0)
                        except:
                            current_price = None
                        watchlist_mgr.add_to_watchlist(ticker=t, added_price=current_price)
                        st.rerun()
    
    with tab2:
        st.markdown("### 📝 Research Notes")
        
        # Save new note
        with st.expander("➕ Save New Research Note", expanded=False):
            note_ticker = st.text_input("Stock Ticker", placeholder="e.g., NVDA", key="note_ticker").upper().strip()
            note_title = st.text_input("Note Title", placeholder="e.g., Q4 Earnings Analysis", key="note_title")
            note_content = st.text_area("Note Content", placeholder="Write your research notes here...", height=150, key="note_content")
            
            if st.button("💾 Save Note", type="primary"):
                if note_ticker and note_title and note_content:
                    result = research_mgr.save_note(
                        ticker=note_ticker,
                        title=note_title,
                        content=note_content,
                        note_type="research"
                    )
                    if result["success"]:
                        st.success(f"✅ Note saved for {note_ticker}!")
                        st.rerun()
                else:
                    st.warning("Please fill in all fields")
        
        st.divider()
        
        # View notes
        col_filter, col_search = st.columns(2)
        with col_filter:
            filter_ticker = st.text_input("Filter by Ticker", placeholder="Leave empty for all", key="filter_notes_ticker").upper().strip()
        with col_search:
            search_query = st.text_input("Search Notes", placeholder="Search in title/content", key="search_notes")
        
        # Get notes
        if search_query:
            notes = research_mgr.search_notes(search_query)
        elif filter_ticker:
            notes = research_mgr.get_notes_for_ticker(filter_ticker)
        else:
            notes = research_mgr.get_all_notes(limit=20)
        
        if notes:
            st.markdown(f"**Found {len(notes)} notes**")
            
            for note in notes:
                with st.expander(f"📄 [{note['ticker']}] {note['title']} - {note['created_at'][:10] if note.get('created_at') else 'N/A'}"):
                    st.markdown(note.get('content', 'No content'))
                    
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_note_{note['id']}"):
                            research_mgr.delete_note(note['id'])
                            st.success("Note deleted")
                            st.rerun()
        else:
            st.info("📝 No research notes yet. Start by saving your first note above!")
    
    with tab3:
        st.markdown("### 📊 Analysis History")
        st.caption("Track your past analyses and insights")
        
        # Get analysis history
        history = research_mgr.get_analysis_history(limit=20)
        
        if history:
            for item in history:
                with st.expander(f"🔍 {item['ticker']} - {item['analysis_type']} ({item['created_at'][:10] if item.get('created_at') else 'N/A'})"):
                    st.markdown(f"**Summary:** {item.get('result_summary', 'No summary')}")
                    if item.get('full_result'):
                        st.text_area("Full Result", item['full_result'], height=100, disabled=True, key=f"history_{item['id']}")
        else:
            st.info("📊 No analysis history yet. Your analyses will appear here as you use the platform.")
    
    # Tips
    with st.expander("💡 Watchlist Tips"):
        st.markdown("""
        **Managing Your Watchlist:**
        - Add stocks with target prices to track your investment thesis
        - Use quick notes to remember why you added a stock
        - Review the Change % to see performance since you added
        
        **Research Notes:**
        - Save detailed analysis for future reference
        - Search notes by ticker or keywords
        - Track your investment research over time
        
        **AI Integration:**
        - Say "Add NVDA to watchlist" in the AI Command Center
        - Ask "Show my watchlist" to see your tracked stocks
        - Request "Save a note for AAPL" to document research
        """)

elif page == "🏦 Ownership":
    from aurelius.functional.ownership import OwnershipIntel
    from aurelius.functional.charting import OwnershipCharts
    import tempfile
    import base64
    
    st.title("🏦 Ownership Analysis")
    st.caption("Institutional ownership, insider trading activity, and shareholder breakdown.")
    
    st.divider()
    
    # Ownership tabs
    own_tab1, own_tab2, own_tab3, own_tab4 = st.tabs([
        "📊 Breakdown", "🏛️ Institutional Holders", "👥 Insider Activity", "🔄 Compare"
    ])
    
    with own_tab1:
        st.subheader("📊 Ownership Breakdown")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Get ownership breakdown
            with st.spinner("Loading ownership data..."):
                breakdown = OwnershipIntel.get_ownership_breakdown(ticker)
            
            if 'error' not in breakdown:
                # Display key metrics
                met_col1, met_col2, met_col3, met_col4 = st.columns(4)
                
                with met_col1:
                    st.metric(
                        "Institutional",
                        f"{breakdown.get('institutions_percent', 0):.1f}%",
                        help="Percentage held by institutions"
                    )
                
                with met_col2:
                    st.metric(
                        "Insiders",
                        f"{breakdown.get('insiders_percent', 0):.1f}%",
                        help="Percentage held by company insiders"
                    )
                
                with met_col3:
                    st.metric(
                        "Public/Other",
                        f"{breakdown.get('public_percent', 0):.1f}%",
                        help="Percentage held by public and other"
                    )
                
                with met_col4:
                    st.metric(
                        "# Institutions",
                        f"{breakdown.get('institutions_count', 0):,}",
                        help="Number of institutional holders"
                    )
                
                st.divider()
                
                # Display pie chart
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp_path = tmp.name
                    OwnershipCharts.ownership_pie_chart(ticker, tmp_path)
                    
                    with open(tmp_path, 'rb') as f:
                        img_data = f.read()
                    st.image(img_data, use_container_width=True)
                    import os
                    os.unlink(tmp_path)
            else:
                st.error(f"Could not load ownership data: {breakdown.get('error', 'Unknown error')}")
        
        with col2:
            st.markdown("""
            <div style="background: rgba(212, 175, 55, 0.05); border: 1px solid rgba(212, 175, 55, 0.2); 
                        border-radius: 12px; padding: 1rem;">
                <h4 style="color: #d4af37; margin: 0 0 0.5rem 0;">Understanding Ownership</h4>
                <p style="color: #a0a0a8; font-size: 0.85rem; margin: 0;">
                    <strong style="color: #fff;">Institutional:</strong> Mutual funds, pension funds, hedge funds, banks, insurance companies.<br><br>
                    <strong style="color: #fff;">Insiders:</strong> Directors, officers, and employees with direct access to company information.<br><br>
                    <strong style="color: #fff;">Public:</strong> Individual investors and others not classified as institutional or insider.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with own_tab2:
        st.subheader("🏛️ Institutional Holders")
        
        holder_col1, holder_col2 = st.columns([3, 1])
        
        with holder_col1:
            holder_type = st.selectbox(
                "Holder Type",
                ["Institutional Holders", "Mutual Fund Holders"],
                help="Select type of holders to view"
            )
        
        with holder_col2:
            top_n = st.number_input("Top N", min_value=5, max_value=20, value=10)
        
        with st.spinner("Loading holder data..."):
            if holder_type == "Institutional Holders":
                holders_df = OwnershipIntel.get_institutional_holders(ticker, top_n)
            else:
                holders_df = OwnershipIntel.get_mutual_fund_holders(ticker, top_n)
        
        if not holders_df.empty and 'error' not in holders_df.columns:
            # Clean up dataframe for display
            display_cols = ['Holder', 'Shares', 'Value (B)', 'Change %', 'Date Reported']
            available_cols = [c for c in display_cols if c in holders_df.columns]
            
            if available_cols:
                st.dataframe(
                    holders_df[available_cols],
                    use_container_width=True,
                    hide_index=True
                )
            
            # Display chart
            st.divider()
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                holder_code = "institutional" if holder_type == "Institutional Holders" else "mutual_fund"
                OwnershipCharts.top_holders_chart(ticker, holder_code, top_n, tmp_path)
                
                with open(tmp_path, 'rb') as f:
                    img_data = f.read()
                st.image(img_data, use_container_width=True)
                import os
                os.unlink(tmp_path)
        else:
            st.info(f"No {holder_type.lower()} data available for {ticker}")
    
    with own_tab3:
        st.subheader("👥 Insider Activity")
        
        with st.spinner("Loading insider data..."):
            insider_summary = OwnershipIntel.get_insider_summary(ticker)
            insider_transactions = OwnershipIntel.get_insider_transactions(ticker, limit=15)
        
        if 'error' not in insider_summary:
            # Display insider metrics
            ins_col1, ins_col2, ins_col3, ins_col4 = st.columns(4)
            
            with ins_col1:
                purchases = insider_summary.get('purchases_shares', 0)
                st.metric(
                    "Purchases",
                    f"{purchases/1e6:.2f}M shares" if purchases else "N/A",
                    help="Total shares purchased by insiders (last 6 months)"
                )
            
            with ins_col2:
                sales = insider_summary.get('sales_shares', 0)
                st.metric(
                    "Sales",
                    f"{sales/1e6:.2f}M shares" if sales else "N/A",
                    help="Total shares sold by insiders (last 6 months)"
                )
            
            with ins_col3:
                net = insider_summary.get('net_shares', 0)
                delta_color = "normal" if net >= 0 else "inverse"
                st.metric(
                    "Net Activity",
                    f"{abs(net)/1e6:.2f}M shares",
                    delta=f"{'Buying' if net > 0 else 'Selling'}" if net != 0 else "Neutral",
                    delta_color=delta_color if net != 0 else "off"
                )
            
            with ins_col4:
                sentiment = insider_summary.get('sentiment', 'N/A')
                sentiment_icon = "🟢" if "Bullish" in sentiment else ("🔴" if "Bearish" in sentiment else "⚪")
                st.metric(
                    "Sentiment",
                    f"{sentiment_icon}",
                    delta=sentiment.replace("(", "").replace(")", ""),
                    delta_color="off"
                )
            
            st.divider()
            
            # Display insider activity chart
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                OwnershipCharts.insider_activity_chart(ticker, tmp_path)
                
                with open(tmp_path, 'rb') as f:
                    img_data = f.read()
                st.image(img_data, use_container_width=True)
                import os
                os.unlink(tmp_path)
            
            # Recent transactions table
            st.subheader("Recent Transactions")
            if not insider_transactions.empty:
                st.dataframe(insider_transactions, use_container_width=True, hide_index=True)
            else:
                st.info("No recent insider transactions found")
        else:
            st.error(f"Could not load insider data: {insider_summary.get('error', 'Unknown error')}")
    
    with own_tab4:
        st.subheader("🔄 Ownership Comparison")
        
        compare_tickers = st.text_input(
            "Compare with (comma-separated tickers)",
            placeholder="e.g., AMD, INTC, QCOM",
            help="Enter ticker symbols to compare ownership structures"
        )
        
        if compare_tickers:
            tickers_list = [t.strip().upper() for t in compare_tickers.split(",") if t.strip()]
            all_tickers = [ticker] + tickers_list
            
            if len(all_tickers) > 1:
                with st.spinner("Loading comparison data..."):
                    comparison_df = OwnershipIntel.get_ownership_comparison(all_tickers)
                
                if not comparison_df.empty:
                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    
                    # Display comparison chart
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        tmp_path = tmp.name
                        OwnershipCharts.ownership_comparison_chart(all_tickers, tmp_path)
                        
                        with open(tmp_path, 'rb') as f:
                            img_data = f.read()
                        st.image(img_data, use_container_width=True)
                        import os
                        os.unlink(tmp_path)
        else:
            st.info("Enter ticker symbols above to compare ownership structures across companies.")
    
    # Tips expander
    with st.expander("💡 Ownership Analysis Tips"):
        st.markdown("""
        **What to Look For:**
        
        1. **High Institutional Ownership (>70%):** Indicates strong professional confidence, but may reduce volatility
        2. **Insider Buying:** Executives buying shares with their own money is often a positive signal
        3. **Insider Selling:** Not always negative - executives often sell for diversification or personal needs
        4. **Concentration Risk:** Very high ownership by few institutions can lead to volatility if they sell
        
        **AI Integration:**
        - Ask "Show me the ownership breakdown for NVDA" in the AI Command Center
        - Request "Who are the top institutional holders of AAPL?"
        - Say "Compare ownership of NVDA, AMD, and INTC"
        """)

elif page == "💰 Valuation":
    from aurelius.functional.dcf import DCFModel
    from aurelius.functional.charting import DCFCharts
    import tempfile
    
    st.title("💰 DCF Valuation Model")
    st.caption("Discounted Cash Flow analysis to estimate intrinsic value per share")
    
    st.divider()
    
    # Tabs for different views
    val_tab1, val_tab2, val_tab3 = st.tabs(["📊 Quick DCF", "🎛️ Custom Model", "📉 Sensitivity"])
    
    with val_tab1:
        st.markdown("### One-Click DCF Valuation")
        st.markdown("Get an instant DCF valuation using automatically calculated assumptions based on historical data.")
        
        if st.button("🚀 Run DCF Analysis", key="quick_dcf", use_container_width=True):
            with st.spinner("Running DCF analysis..."):
                dcf_result = DCFModel.calculate_dcf(ticker)
                
                if "error" in dcf_result:
                    st.error(f"Error: {dcf_result['error']}")
                else:
                    v = dcf_result["valuation"]
                    a = dcf_result["assumptions"]
                    w = dcf_result["wacc_components"]
                    
                    # Key Result Card
                    valuation_color = "#00c896" if v["upside_percent"] > 0 else "#ff4757"
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(13, 13, 18, 0.9) 100%);
                        border: 1px solid {valuation_color};
                        border-radius: 16px;
                        padding: 2rem;
                        text-align: center;
                        margin-bottom: 1.5rem;
                    ">
                        <p style="color: #a0a0a8; font-size: 0.9rem; margin-bottom: 0.5rem;">INTRINSIC VALUE</p>
                        <h1 style="color: #d4af37; font-size: 3.5rem; margin: 0; font-weight: 700;">${v['intrinsic_value_per_share']:.2f}</h1>
                        <p style="color: #a0a0a8; font-size: 1rem; margin-top: 0.5rem;">
                            Current Price: <span style="color: white; font-weight: 600;">${v['current_price']:.2f}</span>
                        </p>
                        <p style="
                            color: {valuation_color}; 
                            font-size: 1.5rem; 
                            font-weight: 700;
                            margin-top: 1rem;
                            padding: 0.5rem 1rem;
                            background: rgba(0, 0, 0, 0.3);
                            border-radius: 8px;
                            display: inline-block;
                        ">
                            {v['upside_percent']:+.1f}% • {v['valuation_status']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Metrics Row
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Enterprise Value", f"${v['enterprise_value']:.1f}B")
                    with col2:
                        st.metric("Equity Value", f"${v['equity_value']:.1f}B")
                    with col3:
                        st.metric("WACC", f"{a['wacc']}%")
                    with col4:
                        st.metric("Terminal Growth", f"{a['terminal_growth_rate']}%")
                    
                    st.divider()
                    
                    # Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📊 Valuation Waterfall")
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                            DCFCharts.valuation_waterfall(ticker, tmp.name)
                            st.image(tmp.name)
                    
                    with col2:
                        st.markdown("#### 📈 FCF Projections")
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                            DCFCharts.projection_chart(ticker, tmp.name)
                            st.image(tmp.name)
                    
                    # Assumptions Breakdown
                    st.markdown("### 📋 Key Assumptions")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Revenue Growth (5-Year)**")
                        growth_df_data = {
                            "Year": [f"Year {i+1}" for i in range(5)],
                            "Growth Rate": [f"{g}%" for g in a['revenue_growth_rates']]
                        }
                        st.dataframe(growth_df_data, use_container_width=True, hide_index=True)
                    
                    with col2:
                        st.markdown("**WACC Components**")
                        wacc_data = {
                            "Component": ["Cost of Equity", "Cost of Debt (after-tax)", "Equity Weight", "Debt Weight", "Beta"],
                            "Value": [f"{w['cost_of_equity']}%", f"{w['cost_of_debt_after_tax']}%", 
                                     f"{w['equity_weight']}%", f"{w['debt_weight']}%", f"{w['beta']}"]
                        }
                        st.dataframe(wacc_data, use_container_width=True, hide_index=True)
    
    with val_tab2:
        st.markdown("### Custom DCF Model")
        st.markdown("Adjust assumptions to run your own DCF scenario.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Revenue Growth Assumptions**")
            y1_growth = st.slider("Year 1 Growth %", -20, 50, 15, key="y1g")
            y2_growth = st.slider("Year 2 Growth %", -20, 50, 12, key="y2g")
            y3_growth = st.slider("Year 3 Growth %", -20, 50, 10, key="y3g")
            y4_growth = st.slider("Year 4 Growth %", -20, 50, 8, key="y4g")
            y5_growth = st.slider("Year 5 Growth %", -20, 50, 6, key="y5g")
        
        with col2:
            st.markdown("**Discount Rate & Terminal Value**")
            custom_wacc = st.slider("WACC Override %", 5.0, 20.0, 10.0, 0.5, key="cwacc")
            custom_terminal = st.slider("Terminal Growth %", 0.0, 5.0, 2.5, 0.5, key="ctg")
        
        if st.button("🧮 Calculate Custom DCF", use_container_width=True, key="custom_dcf"):
            with st.spinner("Calculating custom DCF..."):
                custom_growth = [y1_growth/100, y2_growth/100, y3_growth/100, y4_growth/100, y5_growth/100]
                
                dcf_result = DCFModel.calculate_dcf(
                    ticker,
                    projection_years=5,
                    revenue_growth_rates=custom_growth,
                    terminal_growth_rate=custom_terminal/100,
                    wacc_override=custom_wacc/100
                )
                
                if "error" in dcf_result:
                    st.error(f"Error: {dcf_result['error']}")
                else:
                    v = dcf_result["valuation"]
                    
                    # Result
                    valuation_color = "#00c896" if v["upside_percent"] > 0 else "#ff4757"
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Intrinsic Value", f"${v['intrinsic_value_per_share']:.2f}")
                    with col2:
                        st.metric("Current Price", f"${v['current_price']:.2f}")
                    with col3:
                        st.metric("Upside/Downside", f"{v['upside_percent']:+.1f}%", 
                                 delta=v['valuation_status'], delta_color="normal" if v["upside_percent"] > 0 else "inverse")
                    
                    # Waterfall Chart
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        DCFCharts.valuation_waterfall(ticker, tmp.name)
                        st.image(tmp.name)
    
    with val_tab3:
        st.markdown("### Sensitivity Analysis")
        st.markdown("See how intrinsic value changes with different WACC and terminal growth assumptions.")
        
        col1, col2 = st.columns(2)
        with col1:
            wacc_min = st.number_input("WACC Min %", 5.0, 15.0, 8.0, 0.5)
            wacc_max = st.number_input("WACC Max %", 8.0, 20.0, 14.0, 0.5)
        with col2:
            growth_min = st.number_input("Terminal Growth Min %", 0.0, 3.0, 1.5, 0.5)
            growth_max = st.number_input("Terminal Growth Max %", 2.0, 5.0, 4.0, 0.5)
        
        if st.button("📊 Generate Sensitivity Matrix", use_container_width=True, key="sens_matrix"):
            with st.spinner("Generating sensitivity analysis..."):
                sensitivity = DCFModel.sensitivity_analysis(
                    ticker,
                    wacc_range=(wacc_min/100, wacc_max/100),
                    growth_range=(growth_min/100, growth_max/100),
                    steps=5
                )
                
                if "error" in sensitivity:
                    st.error(f"Error: {sensitivity['error']}")
                else:
                    st.markdown(f"**Current Price: ${sensitivity['current_price']:.2f}**")
                    
                    # Heatmap
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        DCFCharts.sensitivity_heatmap(ticker, tmp.name)
                        st.image(tmp.name)
                    
                    # Matrix Table
                    st.markdown("#### 📋 Value Matrix ($/share)")
                    
                    # Build dataframe
                    import pandas as pd
                    matrix_df = pd.DataFrame(
                        sensitivity["matrix"],
                        index=sensitivity["wacc_values"],
                        columns=sensitivity["growth_values"]
                    )
                    matrix_df.index.name = "WACC \\ Growth"
                    
                    st.dataframe(matrix_df, use_container_width=True)
                    
                    # Interpretation
                    st.info("""
                    **How to Read:**
                    - 🟢 Green cells = Stock appears undervalued at those assumptions
                    - 🔴 Red cells = Stock appears overvalued at those assumptions
                    - Higher WACC = Lower intrinsic value (future cash flows worth less)
                    - Higher Terminal Growth = Higher intrinsic value (more long-term value)
                    """)
    
    # Tips Section
    with st.expander("💡 DCF Model Guide"):
        st.markdown("""
        ### Understanding DCF Valuation
        
        **Key Concepts:**
        1. **Free Cash Flow (FCF):** Cash available after operations and capital expenditures
        2. **WACC:** Weighted Average Cost of Capital - the discount rate reflecting risk
        3. **Terminal Value:** Value of all cash flows beyond the projection period
        4. **Present Value:** Future cash flows discounted back to today
        
        **WACC Components:**
        - Cost of Equity = Risk-Free Rate + Beta × Market Risk Premium
        - Cost of Debt = Interest Rate × (1 - Tax Rate)
        - Weighted by market value of equity and debt
        
        **Limitations:**
        - Very sensitive to growth and discount rate assumptions
        - Terminal value often dominates the result (60-80% of value)
        - Historical data may not predict future performance
        - Works best for stable, cash-generating businesses
        
        **AI Integration:**
        - Ask "Run a DCF analysis on AAPL" in the AI Command Center
        - Request "What's the intrinsic value of NVDA based on DCF?"
        - Say "Show me sensitivity analysis for MSFT valuation"
        """)

elif page == "📊 Risk Lab":
    from aurelius.functional.risk import RiskAnalytics
    from aurelius.functional.charting import RiskCharts
    import tempfile
    
    st.title("📊 Risk Analytics Lab")
    st.caption("Comprehensive risk metrics: VaR, Sharpe Ratio, Drawdown, Volatility, Beta & Alpha")
    
    st.divider()
    
    # Tabs for different views
    risk_tab1, risk_tab2, risk_tab3, risk_tab4 = st.tabs(["📊 Overview", "📉 Drawdown", "🌊 Volatility", "🔗 Correlation"])
    
    with risk_tab1:
        st.markdown("### Risk Overview")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            risk_period = st.selectbox("Analysis Period", ["1y", "6m", "3m", "2y"], index=0, key="risk_period")
        with col2:
            benchmark = st.text_input("Benchmark", value="SPY", key="risk_benchmark")
        
        if st.button("🚀 Run Risk Analysis", use_container_width=True, key="run_risk"):
            with st.spinner("Calculating risk metrics..."):
                # Get all risk metrics
                var = RiskAnalytics.calculate_var(ticker, period=risk_period)
                sharpe = RiskAnalytics.calculate_sharpe_ratio(ticker, period=risk_period)
                drawdown = RiskAnalytics.calculate_max_drawdown(ticker, period=risk_period)
                volatility = RiskAnalytics.calculate_volatility(ticker, period=risk_period)
                beta_alpha = RiskAnalytics.calculate_beta_alpha(ticker, benchmark=benchmark, period=risk_period)
                
                has_error = any("error" in x for x in [var, sharpe, drawdown, volatility, beta_alpha])
                
                if has_error:
                    st.error("Error calculating risk metrics. Please check the ticker symbol.")
                else:
                    # Risk Score Card
                    risk_color = "#ff4757" if volatility['risk_level'] in ["High", "Very High"] else "#00c896" if volatility['risk_level'] in ["Low", "Very Low"] else "#d4af37"
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(13, 13, 18, 0.9) 100%);
                        border: 1px solid {risk_color};
                        border-radius: 16px;
                        padding: 2rem;
                        text-align: center;
                        margin-bottom: 1.5rem;
                    ">
                        <p style="color: #a0a0a8; font-size: 0.9rem; margin-bottom: 0.5rem;">RISK LEVEL</p>
                        <h1 style="color: {risk_color}; font-size: 2.5rem; margin: 0; font-weight: 700;">{volatility['risk_level'].upper()}</h1>
                        <p style="color: #a0a0a8; font-size: 1rem; margin-top: 0.5rem;">
                            Annual Volatility: <span style="color: white; font-weight: 600;">{volatility['historical_volatility_percent']}%</span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Key Metrics Row 1
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("VaR (95%, 1-Day)", f"{var['var_percent']}%", f"${var['var_dollar_per_share']}/share")
                    with col2:
                        st.metric("Sharpe Ratio", f"{sharpe['sharpe_ratio']}", sharpe['interpretation'][:20])
                    with col3:
                        st.metric("Max Drawdown", f"{drawdown['max_drawdown_percent']}%")
                    with col4:
                        st.metric("Beta", f"{beta_alpha['beta']}", beta_alpha['beta_interpretation'][:20])
                    
                    # Key Metrics Row 2
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Sortino Ratio", f"{sharpe['sortino_ratio']}")
                    with col2:
                        st.metric("Annual Return", f"{sharpe['annual_return_percent']}%")
                    with col3:
                        st.metric("Alpha", f"{beta_alpha['alpha_percent']}%")
                    with col4:
                        st.metric("Correlation", f"{beta_alpha['correlation']}")
                    
                    st.divider()
                    
                    # VaR Distribution Chart
                    st.markdown("### 📊 Value at Risk Distribution")
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        RiskCharts.var_distribution_chart(ticker, tmp.name)
                        st.image(tmp.name)
                    
                    # Detailed Breakdown
                    st.markdown("### 📋 Detailed Risk Breakdown")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Value at Risk**")
                        var_data = {
                            "Metric": ["95% VaR", "99% VaR (Est)", "CVaR (Expected Shortfall)", "Current Price"],
                            "Value": [f"{var['var_percent']}%", f"{var['var_percent'] * 1.5:.2f}%", f"{var['cvar_percent']}%", f"${var['current_price']}"]
                        }
                        st.dataframe(var_data, use_container_width=True, hide_index=True)
                        
                        st.markdown("**Performance Attribution**")
                        perf_data = {
                            "Metric": ["Annual Return", "Risk-Free Rate", "Excess Return", "Expected Return (CAPM)", "Alpha"],
                            "Value": [f"{sharpe['annual_return_percent']}%", f"{sharpe['risk_free_rate_percent']}%", 
                                     f"{sharpe['annual_return_percent'] - sharpe['risk_free_rate_percent']:.2f}%",
                                     f"{beta_alpha['expected_return_percent']}%", f"{beta_alpha['alpha_percent']}%"]
                        }
                        st.dataframe(perf_data, use_container_width=True, hide_index=True)
                    
                    with col2:
                        st.markdown("**Volatility Metrics**")
                        vol_data = {
                            "Metric": ["Historical Vol (Annual)", "Current Rolling Vol", "Vol Percentile", "Max Vol (Period)", "Min Vol (Period)"],
                            "Value": [f"{volatility['historical_volatility_percent']}%", f"{volatility['current_rolling_volatility_percent']}%", 
                                     f"{volatility['volatility_percentile']}th", f"{volatility['max_rolling_volatility_percent']}%", 
                                     f"{volatility['min_rolling_volatility_percent']}%"]
                        }
                        st.dataframe(vol_data, use_container_width=True, hide_index=True)
                        
                        st.markdown("**Market Sensitivity**")
                        beta_data = {
                            "Metric": ["Beta", "R-Squared", "Correlation", "Benchmark Return"],
                            "Value": [f"{beta_alpha['beta']}", f"{beta_alpha['r_squared']}", 
                                     f"{beta_alpha['correlation']}", f"{beta_alpha['market_annual_return_percent']}%"]
                        }
                        st.dataframe(beta_data, use_container_width=True, hide_index=True)
    
    with risk_tab2:
        st.markdown("### 📉 Drawdown Analysis")
        st.markdown("Visualize peak-to-trough declines and recovery patterns.")
        
        dd_period = st.selectbox("Period", ["1y", "2y", "6m", "3m"], index=0, key="dd_period")
        
        if st.button("📉 Generate Drawdown Chart", use_container_width=True, key="gen_dd"):
            with st.spinner("Generating drawdown analysis..."):
                dd = RiskAnalytics.calculate_max_drawdown(ticker, period=dd_period)
                
                if "error" in dd:
                    st.error(f"Error: {dd['error']}")
                else:
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Max Drawdown", f"{dd['max_drawdown_percent']}%")
                    with col2:
                        st.metric("Peak Price", f"${dd['peak_price']}")
                    with col3:
                        st.metric("Trough Price", f"${dd['trough_price']}")
                    with col4:
                        st.metric("Current DD", f"{dd['current_drawdown_percent']}%")
                    
                    # Chart
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        RiskCharts.drawdown_chart(ticker, dd_period, tmp.name)
                        st.image(tmp.name)
                    
                    st.info(f"""
                    **Interpretation:**
                    - Max Drawdown occurred from **{dd['max_drawdown_peak_date']}** to **{dd['max_drawdown_trough_date']}**
                    - Recovery: **{'Yes' if dd['recovered'] else 'No'}** {f"(took {dd['recovery_days']} days)" if dd['recovery_days'] else ""}
                    - Average Drawdown: **{dd['average_drawdown_percent']}%**
                    """)
    
    with risk_tab3:
        st.markdown("### 🌊 Volatility Analysis")
        st.markdown("Track historical and rolling volatility trends.")
        
        col1, col2 = st.columns(2)
        with col1:
            vol_period = st.selectbox("Period", ["1y", "2y", "6m"], index=0, key="vol_period")
        with col2:
            vol_window = st.slider("Rolling Window (Days)", 10, 60, 30, key="vol_window")
        
        if st.button("🌊 Generate Volatility Chart", use_container_width=True, key="gen_vol"):
            with st.spinner("Generating volatility analysis..."):
                vol = RiskAnalytics.calculate_volatility(ticker, period=vol_period, window=vol_window)
                
                if "error" in vol:
                    st.error(f"Error: {vol['error']}")
                else:
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Historical Vol", f"{vol['historical_volatility_percent']}%")
                    with col2:
                        st.metric("Current Rolling", f"{vol['current_rolling_volatility_percent']}%")
                    with col3:
                        st.metric("Percentile", f"{vol['volatility_percentile']}th")
                    with col4:
                        st.metric("Risk Level", vol['risk_level'])
                    
                    # Chart
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        RiskCharts.rolling_volatility_chart(ticker, vol_period, vol_window, tmp.name)
                        st.image(tmp.name)
    
    with risk_tab4:
        st.markdown("### 🔗 Correlation Analysis")
        st.markdown("Analyze how stocks move together - useful for portfolio diversification.")
        
        corr_tickers = st.text_input("Enter tickers (comma-separated)", value=f"{ticker},AAPL,MSFT,GOOGL,SPY", key="corr_tickers")
        corr_period = st.selectbox("Period", ["1y", "2y", "6m", "3m"], index=0, key="corr_period")
        
        if st.button("🔗 Generate Correlation Matrix", use_container_width=True, key="gen_corr"):
            with st.spinner("Calculating correlations..."):
                tickers_list = [t.strip().upper() for t in corr_tickers.split(",")]
                
                corr = RiskAnalytics.correlation_matrix(tickers_list, period=corr_period)
                
                if "error" in corr:
                    st.error(f"Error: {corr['error']}")
                else:
                    # Summary
                    if corr.get("highest_correlation"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Highest Correlation", 
                                     f"{corr['highest_correlation']['pair']}", 
                                     f"{corr['highest_correlation']['correlation']}")
                        with col2:
                            st.metric("Lowest Correlation", 
                                     f"{corr['lowest_correlation']['pair']}", 
                                     f"{corr['lowest_correlation']['correlation']}")
                    
                    # Chart
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        RiskCharts.correlation_heatmap(tickers_list, corr_period, tmp.name)
                        st.image(tmp.name)
                    
                    # Correlation Table
                    st.markdown("#### All Correlation Pairs")
                    import pandas as pd
                    pairs_df = pd.DataFrame(corr['all_pairs'])
                    pairs_df['correlation'] = pairs_df['correlation'].apply(lambda x: f"{x:.3f}")
                    st.dataframe(pairs_df, use_container_width=True, hide_index=True)
                    
                    st.info("""
                    **Interpretation:**
                    - **+1.0**: Perfect positive correlation (move together)
                    - **0.0**: No correlation (independent)
                    - **-1.0**: Perfect negative correlation (move opposite)
                    - For diversification, look for low or negative correlations
                    """)
    
    # Tips Section
    with st.expander("💡 Risk Analytics Guide"):
        st.markdown("""
        ### Understanding Risk Metrics
        
        **Value at Risk (VaR):**
        - 95% VaR = "We're 95% confident the loss won't exceed this amount"
        - CVaR (Expected Shortfall) = Average loss when VaR is exceeded
        
        **Sharpe & Sortino Ratios:**
        - Sharpe > 1: Good risk-adjusted returns
        - Sharpe > 2: Excellent risk-adjusted returns
        - Sortino only penalizes downside volatility (more investor-friendly)
        
        **Maximum Drawdown:**
        - Largest peak-to-trough decline
        - Critical for understanding worst-case scenarios
        - Recovery time matters for liquidity planning
        
        **Beta:**
        - Beta = 1: Moves with market
        - Beta > 1: More volatile than market (aggressive)
        - Beta < 1: Less volatile than market (defensive)
        
        **Alpha:**
        - Positive Alpha = Outperformance vs CAPM expectation
        - Negative Alpha = Underperformance
        
        **AI Integration:**
        - Ask "What's the risk profile of NVDA?" in the AI Command Center
        - Request "Show me the drawdown analysis for AAPL"
        - Say "Compare volatility of NVDA, AMD, and INTC"
        """)

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
    
    # Import OpenAI and Agent Library
    try:
        from openai import OpenAI
        
        # Load API key (from Streamlit secrets or local config)
        openai_key = get_openai_key()
        openai_available = openai_key and not openai_key.startswith('<') and not openai_key.startswith('sk-your')
    except:
        openai_available = False
    
    # Load agent library
    from aurelius.agents.agent_library import library as agent_library
    
    # Agent info for UI
    AGENT_UI_INFO = {
        'Market_Analyst': {
            'display_name': '📈 Market Analyst',
            'short_desc': 'Real-time market data, company profiles, and news analysis',
            'tools': ['Company Profile', 'Company News', 'Financials', 'Stock Data'],
            'icon': '📈'
        },
        'Expert_Investor': {
            'display_name': '💼 Expert Investor',
            'short_desc': 'Deep SEC filings analysis and comprehensive financial reports',
            'tools': ['SEC Reports', 'PDF Reports', 'Income Analysis', 'Charts'],
            'icon': '💼'
        },
        'Financial_Analyst': {
            'display_name': '📊 Financial Analyst',
            'short_desc': 'General financial analysis and data interpretation',
            'tools': ['Data Analysis', 'Financial Modeling'],
            'icon': '📊'
        },
        'Data_Analyst': {
            'display_name': '🔢 Data Analyst',
            'short_desc': 'Quantitative analysis and statistical insights',
            'tools': ['Statistical Analysis', 'Data Processing'],
            'icon': '🔢'
        },
        'Statistician': {
            'display_name': '📉 Statistician',
            'short_desc': 'Statistical modeling and probability analysis',
            'tools': ['Probability Models', 'Statistical Tests'],
            'icon': '📉'
        }
    }
    
    # Filter agents to show only financially-relevant ones
    available_agents = ['Market_Analyst', 'Expert_Investor', 'Financial_Analyst', 'Data_Analyst', 'Statistician']
    
    # Agent selection
    col_agent, col_info = st.columns([2, 3])
    
    with col_agent:
        st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; font-weight: 600;'>Select AI Agent</p>", unsafe_allow_html=True)
    agent_type = st.selectbox(
            "Agent Type",
            available_agents,
            format_func=lambda x: AGENT_UI_INFO.get(x, {}).get('display_name', x),
            label_visibility="collapsed"
        )
    
    with col_info:
        agent_info = AGENT_UI_INFO.get(agent_type, {})
        agent_profile = agent_library.get(agent_type, {}).get('profile', 'No profile available')
        
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 12px; padding: 1rem;">
            <div style="color: #d4af37; font-weight: 600; margin-bottom: 0.5rem;">{agent_info.get('short_desc', '')}</div>
            <div style="color: #6a6a72; font-size: 0.8rem;">
                <strong>Tools:</strong> {', '.join(agent_info.get('tools', []))}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
            st.error("⚠️ OpenAI API key not configured. Add your key to Streamlit secrets or OAI_CONFIG_LIST")
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

                    # Call OpenAI with agent-specific profile
                    status_text.markdown(f"**🤖 {AGENT_UI_INFO.get(agent_type, {}).get('display_name', 'AI')} analyzing...**")
                    progress_bar.progress(85)
                    
                    client = OpenAI(api_key=openai_key)
                    
                    # Get agent profile for system message
                    agent_profile_text = agent_library.get(agent_type, {}).get('profile', 
                        "You are an expert financial analyst specializing in stock market analysis.")
                    
                    # Add specific instructions based on agent type
                    if agent_type == 'Market_Analyst':
                        system_content = agent_profile_text + "\n\nFocus on real-time market data, news impact, and short-term trading signals. Provide data-driven insights with specific numbers."
                    elif agent_type == 'Expert_Investor':
                        system_content = agent_profile_text + "\n\nProvide comprehensive analysis suitable for long-term investment decisions. Focus on fundamentals, SEC filings insights, and risk assessment."
                    elif agent_type == 'Statistician':
                        system_content = agent_profile_text + "\n\nFocus on statistical analysis, probability distributions, and quantitative metrics. Include confidence intervals where appropriate."
                    else:
                        system_content = agent_profile_text + "\n\nProvide data-driven financial analysis with specific numbers and clear reasoning."
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_content},
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
                    agent_display = AGENT_UI_INFO.get(agent_type, {}).get('display_name', 'AI Agent')
                    st.success(f"✅ Analysis complete for {ticker} by {agent_display}! Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("Make sure your OpenAI API key is valid and has sufficient credits.")

elif page == "⚔️ Backtest Arena":
    st.markdown("## ⚔️ Backtest Arena")
    st.markdown("Test trading strategies against historical data to evaluate performance before deploying real capital.")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Strategy info
    from aurelius.functional.strategies import STRATEGY_INFO
    
    # Strategy Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; font-weight: 600;'>Strategy</p>", unsafe_allow_html=True)
        strategy_key = st.selectbox(
            "Strategy",
            list(STRATEGY_INFO.keys()),
            format_func=lambda x: STRATEGY_INFO[x]['name'],
            label_visibility="collapsed"
        )
        
        # Show strategy description
        st.markdown(f"""
        <div style="background: rgba(212, 175, 55, 0.05); border: 1px solid rgba(212, 175, 55, 0.1); border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem;">
            <div style="color: #a0a0a8; font-size: 0.8rem;">{STRATEGY_INFO[strategy_key]['description']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 1rem 0 0.5rem 0; font-weight: 600;'>Initial Capital ($)</p>", unsafe_allow_html=True)
        initial_capital = st.number_input(
            "Initial Capital",
            min_value=1000,
            max_value=1000000,
            value=10000,
            step=1000,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; font-weight: 600;'>Strategy Parameters</p>", unsafe_allow_html=True)
        
        # Dynamic parameters based on strategy
        strategy_params_dict = {}
        
        if strategy_key == "SMA_CrossOver":
            fast_ma = st.slider("Fast MA Period", min_value=5, max_value=50, value=10)
            slow_ma = st.slider("Slow MA Period", min_value=20, max_value=200, value=30)
            strategy_params_dict = {"fast": fast_ma, "slow": slow_ma}
            
        elif strategy_key == "RSI":
            rsi_period = st.slider("RSI Period", min_value=7, max_value=28, value=14)
            oversold = st.slider("Oversold Level", min_value=10, max_value=40, value=30)
            overbought = st.slider("Overbought Level", min_value=60, max_value=90, value=70)
            strategy_params_dict = {"period": rsi_period, "oversold": oversold, "overbought": overbought}
            
        elif strategy_key == "MACD":
            fast_period = st.slider("Fast EMA Period", min_value=8, max_value=20, value=12)
            slow_period = st.slider("Slow EMA Period", min_value=20, max_value=35, value=26)
            signal_period = st.slider("Signal Period", min_value=5, max_value=15, value=9)
            strategy_params_dict = {"fast_period": fast_period, "slow_period": slow_period, "signal_period": signal_period}
            
        elif strategy_key == "BollingerBands":
            bb_period = st.slider("MA Period", min_value=10, max_value=50, value=20)
            bb_devfactor = st.slider("Std Dev Factor", min_value=1.0, max_value=3.0, value=2.0, step=0.1)
            strategy_params_dict = {"period": bb_period, "devfactor": bb_devfactor}
            
        elif strategy_key == "MA_Ribbon":
            st.info("MA Ribbon uses fixed EMA periods: 10, 20, 50, 100")
            strategy_params_dict = {}
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Backtest Configuration Summary
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-title">📋 Backtest Configuration</div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
            <div>
                <div class="metric-label">Asset</div>
                <div style="color: #d4af37; font-size: 1.1rem; font-weight: 600;">{ticker}</div>
            </div>
            <div>
                <div class="metric-label">Strategy</div>
                <div style="color: #f8f8f8; font-size: 1.1rem; font-weight: 600;">{STRATEGY_INFO[strategy_key]['name']}</div>
            </div>
            <div>
                <div class="metric-label">Period</div>
                <div style="color: #f8f8f8; font-size: 1.1rem; font-weight: 600;">{start_date} to {end_date}</div>
            </div>
            <div>
                <div class="metric-label">Capital</div>
                <div style="color: #00c896; font-size: 1.1rem; font-weight: 600;">${initial_capital:,}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Run Backtest", use_container_width=True):
        with st.spinner("Running backtest simulation..."):
            try:
                # Determine strategy string for BackTrader
                from aurelius.functional.strategies import STRATEGY_REGISTRY
                strategy_string = STRATEGY_REGISTRY.get(strategy_key, strategy_key)
                
                # Convert params dict to JSON string
                import json
                strategy_params = json.dumps(strategy_params_dict) if strategy_params_dict else ''
                
                result = BackTraderUtils.back_test(
                    ticker,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    strategy=strategy_string,
                    strategy_params=strategy_params,
                    cash=float(initial_capital)
                )
                
                # Parse results
                import re
                
                # Extract key metrics from result string
                final_value_match = re.search(r"'Final Portfolio Value': ([\d.]+)", result)
                final_value = float(final_value_match.group(1)) if final_value_match else initial_capital
                
                total_return = ((final_value - initial_capital) / initial_capital) * 100
                
                # Display Results
                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
                st.markdown("### 📊 Backtest Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Starting Value</div>
                        <div class="metric-value" style="font-size: 1.5rem;">${initial_capital:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Final Value</div>
                        <div class="metric-value" style="font-size: 1.5rem;">${final_value:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    change_class = "" if total_return >= 0 else "negative"
                    sign = "+" if total_return >= 0 else ""
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Return</div>
                        <div class="metric-value {change_class}" style="font-size: 1.5rem;">{sign}{total_return:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    profit = final_value - initial_capital
                    change_class = "" if profit >= 0 else "negative"
                    sign = "+" if profit >= 0 else ""
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Profit/Loss</div>
                        <div class="metric-value {change_class}" style="font-size: 1.5rem;">{sign}${profit:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Full Results
                st.markdown("### 📋 Detailed Analysis")
                with st.expander("View Full Backtest Report", expanded=False):
                    st.code(result, language="python")
                
                # Strategy explanation
                st.markdown(f"""
                <div class="feature-card" style="margin-top: 1rem;">
                    <div class="feature-title">💡 Strategy Explanation</div>
                    <div class="feature-desc">
                        <strong>SMA Crossover Strategy</strong> uses two moving averages:<br><br>
                        • <strong>Fast MA ({fast_ma} days)</strong>: Responds quickly to price changes<br>
                        • <strong>Slow MA ({slow_ma} days)</strong>: Smooths out long-term trend<br><br>
                        <strong>Buy Signal:</strong> When fast MA crosses above slow MA (golden cross)<br>
                        <strong>Sell Signal:</strong> When fast MA crosses below slow MA (death cross)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if total_return >= 0:
                    st.success(f"✅ Strategy was profitable with a {total_return:.2f}% return")
                else:
                    st.warning(f"⚠️ Strategy resulted in a {total_return:.2f}% loss")
                    
            except Exception as e:
                st.error(f"Error running backtest: {str(e)}")

elif page == "📑 Report Forge":
    st.markdown("## 📑 Report Forge")
    st.markdown("Generate professional equity research reports with AI-powered analysis and comprehensive financial data.")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Import report utilities
    from aurelius.functional.reportlab import ReportLabUtils
    from aurelius.functional.analyzer import ReportAnalysisUtils
    
    # Report Configuration
    st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; font-weight: 600;'>Report Configuration</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        report_ticker = st.text_input("Stock Symbol", value=ticker, key="report_ticker")
    with col2:
        fiscal_year = st.selectbox("Fiscal Year", ["2024", "2023", "2022", "2021"], index=0)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Initialize session state for report sections
    if 'report_sections' not in st.session_state:
        st.session_state.report_sections = {
            'business_overview': '',
            'market_position': '',
            'operating_results': '',
            'risk_assessment': '',
            'competitors_analysis': ''
        }
    
    # Step 1: Generate Analysis
    st.markdown("### Step 1: Generate Analysis Sections")
    st.markdown("Click each button to generate AI-powered content for that section.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Business Overview", use_container_width=True):
            with st.spinner("Analyzing business..."):
                try:
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                        tmp_path = tmp.name
                    ReportAnalysisUtils.analyze_company_description(report_ticker, fiscal_year, tmp_path)
                    with open(tmp_path, 'r') as f:
                        content = f.read()
                    os.unlink(tmp_path)
                    
                    # Get AI to summarize
                    openai_key = get_openai_key()
                    if openai_key and not openai_key.startswith('<'):
                        from openai import OpenAI
                        client = OpenAI(api_key=openai_key)
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a financial analyst. Provide a concise business overview in 2-3 paragraphs."},
                                {"role": "user", "content": content[:8000]}
                            ],
                            max_tokens=500
                        )
                        st.session_state.report_sections['business_overview'] = response.choices[0].message.content
                        st.success("✅ Business overview generated!")
                    else:
                        st.session_state.report_sections['business_overview'] = content[:1000]
                        st.warning("Using raw data (OpenAI key not configured)")
                except Exception as e:
                    st.error(f"Error: {str(e)[:100]}")
    
    with col2:
        if st.button("📈 Operating Results", use_container_width=True):
            with st.spinner("Analyzing financials..."):
                try:
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                        tmp_path = tmp.name
                    ReportAnalysisUtils.analyze_income_stmt(report_ticker, fiscal_year, tmp_path)
                    with open(tmp_path, 'r') as f:
                        content = f.read()
                    os.unlink(tmp_path)
                    
                    openai_key = get_openai_key()
                    if openai_key and not openai_key.startswith('<'):
                        from openai import OpenAI
                        client = OpenAI(api_key=openai_key)
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a financial analyst. Summarize the operating results in 2-3 paragraphs with key metrics."},
                                {"role": "user", "content": content[:8000]}
                            ],
                            max_tokens=500
                        )
                        st.session_state.report_sections['operating_results'] = response.choices[0].message.content
                        st.success("✅ Operating results generated!")
                    else:
                        st.session_state.report_sections['operating_results'] = content[:1000]
                except Exception as e:
                    st.error(f"Error: {str(e)[:100]}")
    
    with col3:
        if st.button("⚠️ Risk Assessment", use_container_width=True):
            with st.spinner("Analyzing risks..."):
                try:
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                        tmp_path = tmp.name
                    ReportAnalysisUtils.get_risk_assessment(report_ticker, fiscal_year, tmp_path)
                    with open(tmp_path, 'r') as f:
                        content = f.read()
                    os.unlink(tmp_path)
                    
                    openai_key = get_openai_key()
                    if openai_key and not openai_key.startswith('<'):
                        from openai import OpenAI
                        client = OpenAI(api_key=openai_key)
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a financial analyst. Summarize the top 3 risks in 2-3 paragraphs."},
                                {"role": "user", "content": content[:8000]}
                            ],
                            max_tokens=500
                        )
                        st.session_state.report_sections['risk_assessment'] = response.choices[0].message.content
                        st.success("✅ Risk assessment generated!")
                    else:
                        st.session_state.report_sections['risk_assessment'] = content[:1000]
                except Exception as e:
                    st.error(f"Error: {str(e)[:100]}")
    
    # Additional sections row
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Market Position", use_container_width=True):
            with st.spinner("Analyzing market position..."):
                try:
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                        tmp_path = tmp.name
                    ReportAnalysisUtils.analyze_business_highlights(report_ticker, fiscal_year, tmp_path)
                    with open(tmp_path, 'r') as f:
                        content = f.read()
                    os.unlink(tmp_path)
                    
                    openai_key = get_openai_key()
                    if openai_key and not openai_key.startswith('<'):
                        from openai import OpenAI
                        client = OpenAI(api_key=openai_key)
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a financial analyst. Describe the company's market position, competitive advantages, and key markets in 2-3 paragraphs."},
                                {"role": "user", "content": content[:8000]}
                            ],
                            max_tokens=500
                        )
                        st.session_state.report_sections['market_position'] = response.choices[0].message.content
                        st.success("✅ Market position generated!")
                    else:
                        st.session_state.report_sections['market_position'] = content[:1000]
                except Exception as e:
                    st.error(f"Error: {str(e)[:100]}")
    
    with col2:
        if st.button("🏆 Competitor Analysis", use_container_width=True):
            # Manual competitor input since FMP may not work
            st.session_state.report_sections['competitors_analysis'] = f"""
            {report_ticker} competes in a highly competitive market with major players including industry leaders.
            Key competitive factors include product innovation, brand strength, pricing, and distribution channels.
            The company maintains competitive advantages through its strong brand recognition, ecosystem integration,
            and continuous R&D investment. Market share dynamics continue to evolve with technological changes.
            """
            st.success("✅ Competitor analysis placeholder generated!")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Step 2: Preview Sections
    st.markdown("### Step 2: Preview & Edit Sections")
    
    with st.expander("📋 View Generated Sections", expanded=False):
        for section_name, content in st.session_state.report_sections.items():
            st.markdown(f"**{section_name.replace('_', ' ').title()}**")
            if content:
                st.text_area(
                    section_name,
                    value=content,
                    height=150,
                    key=f"edit_{section_name}",
                    label_visibility="collapsed"
                )
            else:
                st.info("Not generated yet")
            st.markdown("---")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Step 3: Generate PDF Report
    st.markdown("### Step 3: Generate PDF Report")
    
    # Check if all sections are filled
    sections_filled = sum(1 for v in st.session_state.report_sections.values() if v)
    st.progress(sections_filled / 5)
    st.markdown(f"<p style='color: #a0a0a8; font-size: 0.85rem;'>{sections_filled}/5 sections completed</p>", unsafe_allow_html=True)
    
    if st.button("📄 Generate PDF Report", use_container_width=True, type="primary"):
        if sections_filled < 3:
            st.warning("Please generate at least 3 sections before creating the report.")
        else:
            with st.spinner("Generating PDF report... This may take a moment."):
                try:
                    # Create temp directory for charts and report
                    report_dir = f"reports/{report_ticker}"
                    os.makedirs(report_dir, exist_ok=True)
                    
                    # Generate charts
                    share_perf_path = f"{report_dir}/share_performance.png"
                    pe_eps_path = f"{report_dir}/pe_eps.png"
                    
                    st.info("📊 Generating charts...")
                    ReportChartUtils.get_share_performance(
                        report_ticker,
                        datetime.now().strftime("%Y-%m-%d"),
                        share_perf_path
                    )
                    
                    ReportChartUtils.get_pe_eps_performance(
                        report_ticker,
                        datetime.now().strftime("%Y-%m-%d"),
                        years=4,
                        save_path=pe_eps_path
                    )
                    
                    st.info("📝 Building PDF report...")
                    
                    # Generate the PDF
                    result = ReportLabUtils.build_annual_report(
                        ticker_symbol=report_ticker,
                        save_path=report_dir,
                        operating_results=st.session_state.report_sections.get('operating_results', 'Analysis pending.'),
                        market_position=st.session_state.report_sections.get('market_position', 'Analysis pending.'),
                        business_overview=st.session_state.report_sections.get('business_overview', 'Analysis pending.'),
                        risk_assessment=st.session_state.report_sections.get('risk_assessment', 'Analysis pending.'),
                        competitors_analysis=st.session_state.report_sections.get('competitors_analysis', 'Analysis pending.'),
                        share_performance_image_path=share_perf_path,
                        pe_eps_performance_image_path=pe_eps_path,
                        filing_date=datetime.now().strftime("%Y-%m-%d")
                    )
                    
                    # Check if PDF was created
                    pdf_path = f"{report_dir}/{report_ticker}_Equity_Research_report.pdf"
                    
                    if os.path.exists(pdf_path):
                        st.success(f"✅ Report generated successfully!")
                        
                        # Provide download link
                        with open(pdf_path, 'rb') as f:
                            pdf_data = f.read()
                        
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_data,
                            file_name=f"{report_ticker}_Equity_Research_Report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        # Show file info
                        pdf_size = os.path.getsize(pdf_path)
                        st.markdown(f"""
                        <div class="feature-card">
                            <div class="feature-title">📄 Report Details</div>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                                <div>
                                    <div class="metric-label">File Size</div>
                                    <div style="color: #d4af37; font-weight: 600;">{pdf_size/1024:.1f} KB</div>
                                </div>
                                <div>
                                    <div class="metric-label">Company</div>
                                    <div style="color: #f8f8f8; font-weight: 600;">{report_ticker}</div>
                                </div>
                                <div>
                                    <div class="metric-label">Generated</div>
                                    <div style="color: #f8f8f8; font-weight: 600;">{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Report generation issue: {result}")
                        
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
    
    # Tips section
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">💡 Report Generation Tips</div>
        <div class="feature-desc">
            <strong>Best Results:</strong><br>
            • Generate all 5 sections for a comprehensive report<br>
            • AI-generated content requires a valid OpenAI API key<br>
            • Some data (like competitor metrics) requires FMP paid tier<br>
            • Reports include auto-generated charts for stock performance and PE/EPS<br>
            • You can edit sections before generating the final PDF
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "📱 Social Pulse":
    st.markdown("## 📱 Social Pulse")
    st.markdown("Track social sentiment from Reddit's financial communities (r/wallstreetbets, r/stocks, r/investing).")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Check Reddit credentials
    import os
    reddit_client_id = os.environ.get("REDDIT_CLIENT_ID")
    reddit_client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    reddit_available = bool(reddit_client_id and reddit_client_secret)
    
    if not reddit_available:
        st.warning("""
        ⚠️ **Reddit API credentials not configured**
        
        To enable live Reddit sentiment analysis:
        1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
        2. Create a "script" type application
        3. Add to Streamlit secrets or environment variables:
           - `REDDIT_CLIENT_ID`
           - `REDDIT_CLIENT_SECRET`
        
        **Demo mode active**: Showing simulated sentiment data below.
        """)
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; font-weight: 600;'>Search Query</p>", unsafe_allow_html=True)
        search_query = st.text_input(
            "Query",
            value=ticker,
            placeholder="Enter stock ticker or company name...",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<p style='color: #a0a0a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; font-weight: 600;'>Time Range (Days)</p>", unsafe_allow_html=True)
        days_back = st.slider("Days", min_value=7, max_value=90, value=30, label_visibility="collapsed")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    if st.button("🔍 Analyze Social Sentiment", use_container_width=True):
        with st.spinner("Gathering social media data..."):
            
            # Sentiment analysis keywords
            bullish_keywords = ['moon', 'buy', 'buying', 'bullish', 'calls', 'long', 'rocket', '🚀', 'tendies', 'gains', 'pump', 'beat', 'crush']
            bearish_keywords = ['sell', 'selling', 'bearish', 'puts', 'short', 'crash', 'dump', 'loss', 'miss', 'tank', 'drop', 'overvalued']
            
            if reddit_available:
                # Live Reddit data
                try:
                    from aurelius.data_source import RedditUtils
                    from datetime import timedelta
                    
                    end_date = datetime.now().strftime("%Y-%m-%d")
                    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
                    
                    posts_df = RedditUtils.get_reddit_posts(
                        query=search_query,
                        start_date=start_date,
                        end_date=end_date,
                        limit=200,
                        selected_columns=['created_utc', 'title', 'score', 'num_comments']
                    )
                    
                    if posts_df is not None and not posts_df.empty:
                        # Calculate sentiment
                        post_sentiments = []
                        for _, row in posts_df.iterrows():
                            title_lower = row['title'].lower()
                            sentiment = 0
                            for word in bullish_keywords:
                                if word in title_lower:
                                    sentiment += 1
                            for word in bearish_keywords:
                                if word in title_lower:
                                    sentiment -= 1
                            post_sentiments.append({
                                'title': row['title'],
                                'score': row['score'],
                                'comments': row['num_comments'],
                                'sentiment': sentiment,
                                'engagement': row['score'] + row['num_comments']
                            })
                        
                        total_posts = len(posts_df)
                        total_engagement = sum(p['engagement'] for p in post_sentiments)
                        weighted_sentiment = sum(p['sentiment'] * p['engagement'] for p in post_sentiments)
                        avg_sentiment = weighted_sentiment / total_engagement if total_engagement > 0 else 0
                        
                        bullish_posts = sum(1 for p in post_sentiments if p['sentiment'] > 0)
                        bearish_posts = sum(1 for p in post_sentiments if p['sentiment'] < 0)
                        neutral_posts = total_posts - bullish_posts - bearish_posts
                        
                    else:
                        st.warning("No posts found for this query in the selected time range.")
                        total_posts = 0
                        
                except Exception as e:
                    st.error(f"Error fetching Reddit data: {str(e)}")
                    total_posts = 0
            else:
                # Demo/Mock data
                import random
                random.seed(hash(search_query))  # Consistent results for same ticker
                
                total_posts = random.randint(50, 200)
                total_engagement = random.randint(10000, 100000)
                bullish_posts = random.randint(20, int(total_posts * 0.6))
                bearish_posts = random.randint(10, int(total_posts * 0.4))
                neutral_posts = total_posts - bullish_posts - bearish_posts
                
                # Generate mock sentiment score
                avg_sentiment = (bullish_posts - bearish_posts) / total_posts * random.uniform(0.8, 1.2)
                
                # Mock post data
                mock_titles = [
                    f"🚀 {search_query} is going to the moon!",
                    f"Why I'm buying more {search_query} today",
                    f"{search_query} earnings beat expectations - bullish!",
                    f"Is {search_query} overvalued at current levels?",
                    f"Sold all my {search_query} - here's why",
                    f"{search_query} technical analysis - breakout incoming",
                    f"YOLO'd my savings into {search_query} calls",
                    f"{search_query} vs competitors - DD inside",
                    f"Why {search_query} will crash next week",
                    f"{search_query} fundamental analysis - undervalued gem"
                ]
                
                post_sentiments = []
                for i, title in enumerate(mock_titles):
                    sentiment = random.choice([-1, 0, 1, 1])  # Slight bullish bias
                    post_sentiments.append({
                        'title': title,
                        'score': random.randint(100, 5000),
                        'comments': random.randint(50, 500),
                        'sentiment': sentiment,
                        'engagement': random.randint(500, 5000)
                    })
            
            if total_posts > 0:
                # Determine overall sentiment
                if avg_sentiment > 0.15:
                    sentiment_label = "BULLISH"
                    sentiment_color = "#00c896"
                    sentiment_emoji = "🟢"
                elif avg_sentiment < -0.15:
                    sentiment_label = "BEARISH"
                    sentiment_color = "#ff4757"
                    sentiment_emoji = "🔴"
                else:
                    sentiment_label = "NEUTRAL"
                    sentiment_color = "#d4af37"
                    sentiment_emoji = "🟡"
                
                # Display results
                st.markdown("### 📊 Sentiment Analysis Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Overall Sentiment</div>
                        <div style="color: {sentiment_color}; font-size: 1.5rem; font-weight: 700;">{sentiment_emoji} {sentiment_label}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Posts</div>
                        <div class="metric-value">{total_posts:,}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Engagement</div>
                        <div class="metric-value">{total_engagement:,}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    sentiment_score_display = f"{avg_sentiment:+.2f}"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Sentiment Score</div>
                        <div style="color: {sentiment_color}; font-size: 1.5rem; font-weight: 700;">{sentiment_score_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
                
                # Sentiment breakdown chart
                st.markdown("### 📈 Sentiment Breakdown")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Pie chart for sentiment distribution
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Bullish', 'Bearish', 'Neutral'],
                        values=[bullish_posts, bearish_posts, neutral_posts],
                        hole=0.5,
                        marker_colors=['#00c896', '#ff4757', '#6a6a72']
                    )])
                    fig_pie.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="DM Sans", color="#a0a0a8"),
                        showlegend=True,
                        height=300,
                        margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="feature-card">
                        <div class="feature-title">Sentiment Distribution</div>
                        <div style="margin-top: 1rem;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="color: #00c896;">🟢 Bullish Posts</span>
                                <span style="color: #00c896; font-weight: 600;">{bullish_posts} ({bullish_posts/total_posts*100:.1f}%)</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="color: #ff4757;">🔴 Bearish Posts</span>
                                <span style="color: #ff4757; font-weight: 600;">{bearish_posts} ({bearish_posts/total_posts*100:.1f}%)</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: #6a6a72;">🟡 Neutral Posts</span>
                                <span style="color: #6a6a72; font-weight: 600;">{neutral_posts} ({neutral_posts/total_posts*100:.1f}%)</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
                
                # Top posts
                st.markdown("### 🔥 Top Posts by Engagement")
                
                # Sort by engagement and show top 5
                sorted_posts = sorted(post_sentiments, key=lambda x: x['engagement'], reverse=True)[:5]
                
                for i, post in enumerate(sorted_posts, 1):
                    sentiment_indicator = "🟢" if post['sentiment'] > 0 else ("🔴" if post['sentiment'] < 0 else "🟡")
                    st.markdown(f"""
                    <div style="background: rgba(30,30,40,0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div style="flex: 1;">
                                <span style="color: #a0a0a8; font-size: 0.8rem;">#{i}</span>
                                <span style="margin-left: 0.5rem;">{sentiment_indicator}</span>
                                <div style="color: #f8f8f8; margin-top: 0.25rem;">{post['title'][:80]}{'...' if len(post['title']) > 80 else ''}</div>
                            </div>
                            <div style="text-align: right; min-width: 100px;">
                                <div style="color: #d4af37; font-weight: 600;">⬆️ {post['score']:,}</div>
                                <div style="color: #6a6a72; font-size: 0.8rem;">💬 {post['comments']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Data source note
                if not reddit_available:
                    st.info("📌 **Demo Mode**: Data shown is simulated. Configure Reddit API credentials for live data.")
                else:
                    st.success(f"✅ Live data from Reddit (last {days_back} days)")

elif page == "📚 Research Library":
    st.markdown("## 📚 Research Library")
    st.markdown("Upload financial documents and ask questions using AI-powered document analysis.")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Check OpenAI availability
    try:
        from openai import OpenAI
        openai_key = get_openai_key()
        openai_available = openai_key and not openai_key.startswith('<') and not openai_key.startswith('sk-your')
    except:
        openai_available = False
    
    if not openai_available:
        st.warning("⚠️ OpenAI API key required for document Q&A. Configure your key in Streamlit secrets or OAI_CONFIG_LIST.")
    
    # Initialize session state for documents
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = {}
    if 'document_chunks' not in st.session_state:
        st.session_state.document_chunks = []
    if 'research_question' not in st.session_state:
        st.session_state.research_question = ""
    
    # Quick Load Section FIRST - most common action
    st.markdown("### 📊 Quick Load Financial Data")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        quick_ticker = st.text_input("Ticker", value=ticker, key="quick_load_ticker", label_visibility="collapsed", placeholder="Ticker...")
    
    with col2:
        if st.button("📄 Income Statement", use_container_width=True):
            try:
                income = YFinanceUtils.get_income_stmt(quick_ticker)
                if income is not None and not income.empty:
                    income_text = f"=== {quick_ticker} INCOME STATEMENT ===\n{income.to_string()}"
                    st.session_state.uploaded_documents[f'{quick_ticker}_income'] = income_text
                    # Re-chunk all documents
                    all_text = "\n\n".join(st.session_state.uploaded_documents.values())
                    st.session_state.document_chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 800) if len(all_text[i:i+1000]) > 100]
                    st.success(f"✅ Loaded income statement")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col3:
        if st.button("📊 Balance Sheet", use_container_width=True):
            try:
                balance = YFinanceUtils.get_balance_sheet(quick_ticker)
                if balance is not None and not balance.empty:
                    balance_text = f"=== {quick_ticker} BALANCE SHEET ===\n{balance.to_string()}"
                    st.session_state.uploaded_documents[f'{quick_ticker}_balance'] = balance_text
                    all_text = "\n\n".join(st.session_state.uploaded_documents.values())
                    st.session_state.document_chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 800) if len(all_text[i:i+1000]) > 100]
                    st.success(f"✅ Loaded balance sheet")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col4:
        if st.button("💵 Cash Flow", use_container_width=True):
            try:
                cashflow = YFinanceUtils.get_cash_flow(quick_ticker)
                if cashflow is not None and not cashflow.empty:
                    cashflow_text = f"=== {quick_ticker} CASH FLOW ===\n{cashflow.to_string()}"
                    st.session_state.uploaded_documents[f'{quick_ticker}_cashflow'] = cashflow_text
                    all_text = "\n\n".join(st.session_state.uploaded_documents.values())
                    st.session_state.document_chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 800) if len(all_text[i:i+1000]) > 100]
                    st.success(f"✅ Loaded cash flow")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Document Status - ALWAYS VISIBLE
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Status bar
    doc_count = len(st.session_state.uploaded_documents)
    chunk_count = len(st.session_state.document_chunks)
    total_chars = sum(len(d) for d in st.session_state.uploaded_documents.values())
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Documents Loaded</div>
            <div class="metric-value">{doc_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Text Chunks</div>
            <div class="metric-value">{chunk_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Characters</div>
            <div class="metric-value">{total_chars:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.uploaded_documents = {}
            st.session_state.document_chunks = []
            st.rerun()
    
    # Show document names if loaded
    if st.session_state.uploaded_documents:
        doc_names = ", ".join(st.session_state.uploaded_documents.keys())
        st.markdown(f"<p style='color: #00c896; font-size: 0.85rem;'>📄 Loaded: {doc_names}</p>", unsafe_allow_html=True)
    else:
        st.info("👆 Click buttons above to load financial statements, or upload/paste documents below.")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Question & Answer Section - Main Feature
    st.markdown("### 💬 Ask Questions About Your Documents")
    
    question = st.text_input(
        "Your Question",
        value=st.session_state.research_question,
        placeholder="e.g., What was the total revenue? How did operating income change?",
        key="research_q_input"
    )
    
    # Sample questions as clickable buttons
    st.markdown("<p style='color: #6a6a72; font-size: 0.8rem; margin-bottom: 0.5rem;'>Quick questions:</p>", unsafe_allow_html=True)
    sample_qs = ["Total Revenue?", "Net Income?", "Operating Expenses?", "Gross Profit Margin?"]
    qcols = st.columns(4)
    for i, sq in enumerate(sample_qs):
        with qcols[i]:
            if st.button(sq, key=f"sq_{i}", use_container_width=True):
                st.session_state.research_question = sq
                st.rerun()
    
    if st.button("🔍 Find Answer", use_container_width=True, type="primary"):
        current_question = question or st.session_state.research_question
        
        if not st.session_state.document_chunks:
            st.warning("⚠️ No documents loaded. Use Quick Load buttons above or upload documents.")
        elif not current_question.strip():
            st.warning("⚠️ Please enter a question.")
        elif not openai_available:
            st.error("⚠️ OpenAI API key required. Configure in Streamlit secrets.")
        else:
            with st.spinner("🔍 Searching documents and generating answer..."):
                try:
                    # Keyword-based retrieval
                    query_words = set(current_question.lower().split())
                    scored_chunks = []
                    
                    for chunk in st.session_state.document_chunks:
                        chunk_words = set(chunk.lower().split())
                        overlap = len(query_words & chunk_words)
                        scored_chunks.append((overlap, chunk))
                    
                    scored_chunks.sort(reverse=True)
                    relevant_chunks = [chunk for _, chunk in scored_chunks[:5]]
                    context = "\n\n---\n\n".join(relevant_chunks)
                    
                    client = OpenAI(api_key=openai_key)
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": """You are a financial analyst assistant. Answer questions based ONLY on the provided financial data.
                                Be specific with numbers. If data isn't available, say so clearly.
                                Format numbers properly (e.g., $1.5B, 15.3%). Use markdown for clarity."""
                            },
                            {
                                "role": "user",
                                "content": f"""Financial Data Context:

{context}

Question: {current_question}

Provide a clear, data-driven answer."""
                            }
                        ],
                        temperature=0.2,
                        max_tokens=800
                    )
                    
                    answer = response.choices[0].message.content
                    
                    st.markdown("### 📝 Answer")
                    st.markdown(f"""
                    <div class="feature-card" style="background: linear-gradient(145deg, rgba(0, 200, 150, 0.1) 0%, rgba(212, 175, 55, 0.1) 100%); border: 1px solid rgba(0, 200, 150, 0.2);">
                        <div style="color: #e0e0e0; line-height: 1.8; font-size: 1rem;">
                            {answer.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("📄 View Source Data Used"):
                        for i, chunk in enumerate(relevant_chunks[:3], 1):
                            st.code(chunk[:600] + "..." if len(chunk) > 600 else chunk, language=None)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Manual Upload Section - Secondary
    with st.expander("📤 Upload Custom Documents"):
        uploaded_files = st.file_uploader(
            "Upload TXT or MD files",
            type=['txt', 'md'],
            accept_multiple_files=True,
            key="research_uploader"
        )
        
        pasted_text = st.text_area(
            "Or paste text directly",
            height=100,
            placeholder="Paste earnings report, SEC filing, or any text...",
            key="research_paste"
        )
        
        if st.button("📥 Process Uploads", use_container_width=True):
            processed = 0
            if uploaded_files:
                for file in uploaded_files:
                    try:
                        content = file.read().decode('utf-8')
                        st.session_state.uploaded_documents[file.name] = content
                        processed += 1
                    except:
                        pass
            
            if pasted_text.strip():
                st.session_state.uploaded_documents['pasted_text'] = pasted_text
                processed += 1
            
            if processed > 0:
                all_text = "\n\n".join(st.session_state.uploaded_documents.values())
                st.session_state.document_chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 800) if len(all_text[i:i+1000]) > 100]
                st.success(f"✅ Processed {processed} document(s)")
                st.rerun()
            else:
                st.warning("No documents to process")
    
    # Tips
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">💡 How to Use</div>
        <div class="feature-desc">
            1. <strong>Load Data</strong>: Click Income Statement, Balance Sheet, or Cash Flow for any ticker<br>
            2. <strong>Ask Questions</strong>: Type a question or click a quick question button<br>
            3. <strong>Get Answers</strong>: AI analyzes loaded documents and provides data-driven answers<br>
            <br>
            <em>Tip: Load multiple financial statements for comprehensive analysis!</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        ">☀️</div>
        <span style="
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            color: #f8f8f8;
        ">IKSHVAKU</span>
    </div>
    <p style="color: #6b6b75; font-size: 0.8rem; margin: 0.5rem 0;">Wealth Intelligence Platform</p>
    <p style="color: #4a4a52; font-size: 0.7rem; margin: 0.25rem 0; font-style: italic;">"धर्मो रक्षति रक्षितः" — Dharma protects those who protect it.</p>
    <div style="display: flex; align-items: center; justify-content: center; gap: 1.5rem; margin-top: 1rem;">
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">Deep Scan</span>
        <span style="color: #4a4a52;">•</span>
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">The Vault</span>
        <span style="color: #4a4a52;">•</span>
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">Signal Wire</span>
        <span style="color: #4a4a52;">•</span>
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">The Oracle</span>
        <span style="color: #4a4a52;">•</span>
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">Backtest</span>
        <span style="color: #4a4a52;">•</span>
        <span style="color: #4a4a52; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">Report Forge</span>
    </div>
</div>
""", unsafe_allow_html=True)

