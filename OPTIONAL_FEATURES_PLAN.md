# AURELIUS - Optional Features Implementation Plan

## Overview

This document outlines a step-by-step approach to test and implement the remaining optional features from the codebase.

---

## 📋 FEATURE CHECKLIST

| # | Feature | Complexity | Dependencies | Priority |
|---|---------|------------|--------------|----------|
| 1 | Renko Charts | Low | mplfinance | High |
| 2 | Point & Figure Charts | Low | mplfinance | High |
| 3 | More Backtest Strategies | Medium | backtrader | Medium |
| 4 | Segment Analysis | Low | YFinance, SEC API | Medium |
| 5 | Multi-Agent Selection | Medium | AutoGen | Medium |
| 6 | Reddit Sentiment | Medium | PRAW, Reddit API | Low |
| 7 | RAG Document Q&A | High | AutoGen, ChromaDB | Low |

---

## 🔬 PHASE 1: Additional Chart Types (Renko & PnF)

### 1.1 Testing - Renko Charts

**What it does:** Renko charts filter out noise by only showing price movements above a certain threshold ("brick size"), ignoring time.

**Test Plan:**
```python
# Test: Renko chart generation
from aurelius.functional import MplFinanceUtils

result = MplFinanceUtils.plot_stock_price_chart(
    ticker_symbol="AAPL",
    start_date="2024-01-01",
    end_date="2024-12-31",
    save_path="test_renko.png",
    type="renko"  # Key parameter
)
```

**Expected Output:** PNG file with Renko brick chart

**Potential Issues:**
- Requires sufficient price movement data
- May need `renko_params` for custom brick size

---

### 1.2 Testing - Point & Figure Charts

**What it does:** PnF charts show price direction changes using X (up) and O (down) columns, filtering minor fluctuations.

**Test Plan:**
```python
# Test: Point & Figure chart generation
result = MplFinanceUtils.plot_stock_price_chart(
    ticker_symbol="AAPL",
    start_date="2024-01-01",
    end_date="2024-12-31",
    save_path="test_pnf.png",
    type="pnf"  # Key parameter
)
```

**Expected Output:** PNG file with Point & Figure chart

---

### 1.3 UI Integration - Deep Scan Enhancement

**Location:** Deep Scan page, Chart Type selector

**Changes:**
- Add "Renko" and "Point & Figure" to chart type dropdown
- Use mplfinance for these specific types (not Plotly)
- Display generated PNG instead of interactive chart

---

## 📊 PHASE 2: Additional Backtest Strategies

### 2.1 Available Strategies

The current implementation supports custom strategies via module import. We can add:

| Strategy | Description | Parameters |
|----------|-------------|------------|
| RSI Overbought/Oversold | Buy when RSI < 30, Sell when RSI > 70 | `period`, `oversold`, `overbought` |
| MACD Crossover | Buy/Sell on MACD signal crossover | `fast`, `slow`, `signal` |
| Bollinger Bands | Trade on band breakouts | `period`, `std_dev` |
| Moving Average Ribbon | Multi-MA trend following | `periods: [10,20,50,100]` |

### 2.2 Testing Plan

**Test Script:** `test_phase4_strategies.py`

```python
import backtrader as bt
from backtrader.indicators import RSI, MACD, BollingerBands

class RSI_Strategy(bt.Strategy):
    params = (('period', 14), ('oversold', 30), ('overbought', 70),)
    
    def __init__(self):
        self.rsi = RSI(period=self.p.period)
    
    def next(self):
        if self.rsi < self.p.oversold and not self.position:
            self.buy()
        elif self.rsi > self.p.overbought and self.position:
            self.sell()

class MACD_Strategy(bt.Strategy):
    params = (('fast', 12), ('slow', 26), ('signal', 9),)
    
    def __init__(self):
        self.macd = MACD(period_me1=self.p.fast, period_me2=self.p.slow, period_signal=self.p.signal)
    
    def next(self):
        if self.macd.macd > self.macd.signal and not self.position:
            self.buy()
        elif self.macd.macd < self.macd.signal and self.position:
            self.sell()
```

### 2.3 UI Integration - Backtest Arena Enhancement

**Location:** Backtest Arena page

**Changes:**
- Add strategy dropdown: SMA Crossover, RSI, MACD, Bollinger Bands
- Dynamic parameter inputs based on strategy selection
- Strategy explanation tooltip

---

## 📈 PHASE 3: Segment Analysis

### 3.1 Testing

**What it does:** Breaks down company revenue by business segment using 10-K filings.

**Test:**
```python
from aurelius.functional import ReportAnalysisUtils

result = ReportAnalysisUtils.analyze_segment_stmt(
    ticker_symbol="MSFT",
    fyear="2023",
    save_path="segment_analysis.txt"
)
```

**Expected Output:** Text file with segment breakdown (Azure, Office, Gaming, etc.)

### 3.2 UI Integration - The Vault Enhancement

**Location:** The Vault → Deep Analysis tab

**Changes:**
- Add "Segment Analysis" sub-section
- Display segment breakdown in table/chart format

---

## 🤖 PHASE 4: Multi-Agent Selection

### 4.1 Available Agent Types

From `agent_library.py`:

| Agent | Capabilities |
|-------|--------------|
| Market_Analyst | Company profiles, news, financials via FinnHub & YFinance |
| Expert_Investor | SEC reports, PDF generation, comprehensive analysis |
| Financial_Analyst | General financial analysis |
| Data_Analyst | Data processing and analysis |

### 4.2 Testing Plan

```python
from aurelius.agents import library

# Test Market Analyst agent
market_analyst = library["Market_Analyst"]
print(f"Profile: {market_analyst['profile']}")
print(f"Tools: {market_analyst.get('toolkits', [])}")
```

### 4.3 UI Integration - Oracle Enhancement

**Location:** The Oracle page

**Changes:**
- Agent type selector dropdown (Market Analyst, Expert Investor, etc.)
- Display agent's capabilities before querying
- Adjust available tools based on agent type

---

## 📱 PHASE 5: Reddit Sentiment (Optional - Requires API Keys)

### 5.1 Prerequisites

Requires Reddit API credentials:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`

Sign up at: https://www.reddit.com/prefs/apps

### 5.2 Testing Plan

```python
from aurelius.data_source import RedditUtils

# Test Reddit post retrieval
posts = RedditUtils.get_reddit_posts(
    query="NVDA",
    start_date="2024-11-01",
    end_date="2024-12-01",
    limit=100
)
print(f"Found {len(posts)} posts")
print(posts.head())
```

**Subreddits Searched:**
- r/wallstreetbets
- r/stocks
- r/investing

### 5.3 UI Integration

**Location:** New section in Command Deck or separate "Sentiment" page

**Features:**
- Ticker search for Reddit mentions
- Post count & score aggregation
- Sentiment trend over time

---

## 🔍 PHASE 6: RAG Document Q&A (Advanced)

### 6.1 What it does

RAG (Retrieval-Augmented Generation) allows querying uploaded documents (PDFs, 10-K filings) with natural language questions.

### 6.2 Prerequisites

- AutoGen with RAG support
- ChromaDB for vector storage
- OpenAI API key

### 6.3 Testing Plan

```python
from aurelius.functional import get_rag_function

retrieve_config = {
    "docs_path": ["path/to/10K_report.pdf"],
    "chunk_size": 1000,
    "get_or_create": True,
}

retrieve_content, rag_agent = get_rag_function(retrieve_config)

# Query the document
answer = retrieve_content(
    message="What are the main risk factors mentioned in this report?",
    n_results=3
)
```

### 6.4 UI Integration

**Location:** New "📚 Research Library" page

**Features:**
- File upload for PDFs
- Natural language query input
- Retrieved context display
- AI-generated answers

---

## 🗓️ IMPLEMENTATION ORDER

### Sprint 1: Quick Wins (Renko, PnF, Segment)
**Estimated Time:** 1-2 hours

1. ✅ Test Renko charts
2. ✅ Test PnF charts
3. ✅ Test Segment Analysis
4. ✅ Add to UI (Deep Scan + The Vault)

### Sprint 2: Backtest Strategies
**Estimated Time:** 2-3 hours

1. ✅ Create RSI strategy class
2. ✅ Create MACD strategy class
3. ✅ Create Bollinger Bands strategy class
4. ✅ Test all strategies
5. ✅ Enhance Backtest Arena UI

### Sprint 3: Multi-Agent Selection
**Estimated Time:** 2-3 hours

1. ✅ Test agent loading
2. ✅ Enhance Oracle UI with agent selection
3. ✅ Wire up different toolkits per agent

### Sprint 4: Reddit Sentiment (If API available)
**Estimated Time:** 2-3 hours

1. ⬜ Setup Reddit API credentials
2. ⬜ Test data retrieval
3. ⬜ Create Sentiment page/section

### Sprint 5: RAG (Advanced)
**Estimated Time:** 4-6 hours

1. ⬜ Verify ChromaDB installation
2. ⬜ Test RAG function
3. ⬜ Create Research Library page

---

## 📝 TESTING COMMANDS

```bash
# Activate environment
cd /Users/viveksingh/Desktop/financial_analysis_agent/aurelius
source /Users/viveksingh/miniconda3/etc/profile.d/conda.sh
conda activate aurelius_test

# Run individual phase tests
python test_phase4_charts.py      # Renko, PnF
python test_phase4_strategies.py  # RSI, MACD, Bollinger
python test_phase4_segment.py     # Segment Analysis
python test_phase4_agents.py      # Multi-agent
python test_phase4_reddit.py      # Reddit (if API available)
python test_phase4_rag.py         # RAG (advanced)
```

---

## ✅ SUCCESS CRITERIA

| Phase | Test Criteria |
|-------|---------------|
| Phase 1 | PNG files generated for Renko & PnF charts |
| Phase 2 | Backtest returns valid metrics for all strategy types |
| Phase 3 | Segment breakdown text generated successfully |
| Phase 4 | Different agents have different tool access |
| Phase 5 | Reddit posts retrieved with sentiment data |
| Phase 6 | RAG answers questions from uploaded documents |

---

*Ready to begin? Start with Phase 1 testing!*

