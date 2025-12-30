---
title: AURELIUS
emoji: 🏛️
colorFrom: yellow
colorTo: green
sdk: streamlit
sdk_version: 1.52.2
app_file: app.py
pinned: false
license: mit
---

<div align="center">

# 🏛️ AURELIUS

### AI-Powered Wealth Intelligence Platform

*"The object of life is not to be on the side of the majority, but to escape finding oneself in the ranks of the insane." — Marcus Aurelius*

</div>

---

## Overview

**AURELIUS** is a sophisticated AI-powered wealth intelligence platform that combines institutional-grade financial analysis with cutting-edge AI agents. Named after the philosopher-emperor Marcus Aurelius, the platform embodies the principles of wisdom, rationality, and strategic thinking in financial decision-making.

## ✨ Features

| Module | Description |
|--------|-------------|
| 🎛️ **Command Deck** | Real-time market overview with price charts, volume analysis, and key metrics |
| 🔬 **Deep Scan** | Comprehensive technical analysis with moving averages, momentum indicators, and trend identification |
| 🏛️ **The Vault** | Financial archives — income statements, balance sheets, and cash flow records |
| 📡 **Signal Wire** | Market intelligence feed with company news, sentiment analysis, and profile data |
| 🔮 **The Oracle** | AI-powered wealth strategist for predictive insights and investment guidance |

## 🚀 Quick Start

### 1. Create Environment

```bash
conda create --name aurelius python=3.10
conda activate aurelius
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

For local development, create `.streamlit/secrets.toml`:

```toml
[openai]
api_key = "your-openai-api-key"

[finnhub]
api_key = "your-finnhub-api-key"

[fmp]
api_key = "your-fmp-api-key"
```

### 4. Launch the Platform

```bash
streamlit run app.py
```

## 📋 API Keys Required

| Provider | Purpose | Get Key |
|----------|---------|---------|
| OpenAI | AI Agent (The Oracle) | [platform.openai.com](https://platform.openai.com) |
| Finnhub | News & Company Data | [finnhub.io](https://finnhub.io) |
| Yahoo Finance | Stock Prices & Financials | Free (built-in) |
| FMP (Optional) | Advanced Metrics | [financialmodelingprep.com](https://financialmodelingprep.com) |

## 🏗️ Architecture

```
AURELIUS
├── app.py                 # Main Streamlit application
├── aurelius/
│   ├── agents/           # AI Agent definitions
│   ├── data_source/      # Market data connectors
│   ├── functional/       # Analysis utilities
│   ├── toolkits.py       # Agent tools
│   └── utils.py          # Helpers
├── configs/              # Configuration files
└── .streamlit/           # Streamlit configuration
```

## 🎨 Design Philosophy

AURELIUS features a premium dark interface with:
- **Gold & Emerald accents** — Representing wealth and growth
- **Glassmorphism effects** — Modern, sophisticated aesthetic
- **Custom typography** — Outfit, DM Sans, IBM Plex Mono
- **Responsive layout** — Optimized for all screen sizes

## 📖 The Oracle: AI Agent

The Oracle is powered by GPT-4 and provides:
- **Market forecasts** with directional predictions
- **Fundamental analysis** of company financials
- **Sentiment analysis** from news and market data
- **Investment guidance** with risk assessment

## ⚠️ Disclaimer

This platform is for educational and research purposes only. It should not be construed as financial advice or recommendations for trading. Always consult with qualified financial professionals before making investment decisions.

---

<div align="center">

**AURELIUS** — *Wisdom Meets Wealth*

</div>
