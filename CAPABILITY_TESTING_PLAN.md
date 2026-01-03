# AURELIUS - Capability Testing & Integration Plan

## Overview

This document outlines the systematic approach to test all hidden capabilities in the codebase before integrating them into the UI.

---

## 🔬 PHASE 1: Core Analysis Capabilities

### 1.1 Report Analysis Utils (`aurelius/functional/analyzer.py`)

| Function | Test Input | Expected Output | API Dependencies |
|----------|------------|-----------------|------------------|
| `analyze_income_stmt` | AAPL, 2023 | Income analysis + 10-K context saved to file | YFinance, SEC API |
| `analyze_balance_sheet` | AAPL, 2023 | Balance sheet analysis saved to file | YFinance, SEC API |
| `analyze_cash_flow` | AAPL, 2023 | Cash flow analysis saved to file | YFinance, SEC API |
| `analyze_segment_stmt` | MSFT, 2023 | Segment breakdown by business | YFinance, SEC API |
| `get_risk_assessment` | NVDA, 2023 | Top 3 risks with detailed breakdown | YFinance, SEC API |
| `get_competitors_analysis` | AAPL, [MSFT, GOOGL], 2023 | Multi-year financial comparison | FMP API (may need paid tier) |
| `analyze_business_highlights` | TSLA, 2023 | Business line performance | SEC API |
| `analyze_company_description` | AMZN, 2023 | Industry overview & strengths | YFinance, SEC API |
| `get_key_data` | AAPL, 2023-10-30 | Key metrics dict (Rating, Price, Market Cap, etc.) | YFinance, FMP API |

**Test Script Location:** `test_phase1_analysis.py`

**Potential Issues to Watch:**
- SEC API rate limits
- FMP API paid tier requirements for some endpoints
- Fiscal year alignment with 10-K filing dates

---

### 1.2 SEC Utils (`aurelius/data_source/sec_utils.py`)

| Function | Test Input | Expected Output |
|----------|------------|-----------------|
| `get_10k_section` | AAPL, 2023, section=1 | Business description text |
| `get_10k_section` | AAPL, 2023, section=1A | Risk factors text |
| `get_10k_section` | AAPL, 2023, section=7 | MD&A text |

**Sections to Test:**
- Section 1: Business
- Section 1A: Risk Factors  
- Section 7: MD&A
- Section 7A: Quantitative & Qualitative Disclosures

---

## 📊 PHASE 2: Backtesting & Charting

### 2.1 BackTrader Utils (`aurelius/functional/quantitative.py`)

| Test Case | Parameters | Expected Output |
|-----------|------------|-----------------|
| Basic SMA Crossover | AAPL, 2022-01-01 to 2023-12-31, SMA_CrossOver | Portfolio value, Sharpe Ratio, Drawdown |
| Custom Strategy | MSFT, custom TestStrategy | Full trade analysis |
| With Visualization | NVDA, save_fig="backtest.png" | Chart file saved |

**Test Script Location:** `test_phase2_backtest.py`

**Metrics to Verify:**
- Starting/Final Portfolio Value
- Sharpe Ratio
- Maximum Drawdown
- Trade count and win rate

---

### 2.2 Charting Utils (`aurelius/functional/charting.py`)

| Function | Test Input | Expected Output |
|----------|------------|-----------------|
| `plot_stock_price_chart` | AAPL, candle, default style | Candlestick PNG |
| `plot_stock_price_chart` | AAPL, ohlc, yahoo style | OHLC PNG |
| `plot_stock_price_chart` | AAPL, line, mav=[20,50] | Line chart with MAs |
| `get_share_performance` | MSFT vs S&P 500, 1 year | Comparison PNG |
| `get_pe_eps_performance` | NVDA, 4 years | PE/EPS dual-axis PNG |

**Chart Types to Test:**
- `candle` - Candlestick
- `ohlc` - OHLC bars
- `line` - Line chart
- `renko` - Renko bricks
- `pnf` - Point & Figure

---

## 📑 PHASE 3: Report Generation & RAG

### 3.1 ReportLab Utils (`aurelius/functional/reportlab.py`)

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Full Annual Report | AAPL with all sections | Professional PDF |

**Required Inputs for PDF Generation:**
1. `ticker_symbol` - Stock ticker
2. `operating_results` - AI-generated income summary
3. `market_position` - AI-generated market analysis
4. `business_overview` - AI-generated business description
5. `risk_assessment` - AI-generated risk analysis
6. `competitors_analysis` - AI-generated competitor comparison
7. `share_performance_image_path` - Pre-generated chart
8. `pe_eps_performance_image_path` - Pre-generated chart
9. `filing_date` - Report date

**Test Script Location:** `test_phase3_reports.py`

---

### 3.2 RAG Function (`aurelius/functional/rag.py`)

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Query 10-K Document | "What are the main revenue sources?" | Retrieved context + answer |
| Query Earnings Call | "What guidance did management provide?" | Retrieved context + answer |

**Dependencies:**
- ChromaDB for vector storage
- OpenAI embeddings
- Document preprocessing

---

## 🎨 PHASE 4: UI Integration Architecture

### Proposed New Pages/Sections

| Page Name | Capabilities Exposed | Priority |
|-----------|---------------------|----------|
| **Deep Analysis Lab** | Income/Balance/Cash analysis, Risk Assessment, Competitor Analysis | HIGH |
| **Backtest Arena** | Strategy backtesting with visual results | HIGH |
| **Chart Studio** | Advanced charts (candlestick, OHLC, PE/EPS) | MEDIUM |
| **Report Forge** | PDF equity research report generation | MEDIUM |
| **Document Oracle** | RAG-based document Q&A | LOW |

### UI Component Mapping

```
Current UI                    New Capabilities
─────────────────────────────────────────────────────
Command Deck (Dashboard)  →   Add: PE/EPS chart, Stock vs S&P comparison
Deep Scan (Stock)         →   Add: Candlestick charts, technical indicators
The Vault (Financials)    →   Add: Deep analysis (Income, Balance, Cash), Segment analysis
Signal Wire (News)        →   Add: Risk Assessment highlights
The Oracle (AI Agent)     →   Add: Agent type selector, Report generation
─────────────────────────────────────────────────────
NEW: Backtest Arena       →   Full backtesting UI
NEW: Report Forge         →   PDF generation workflow
```

---

## 🚀 PHASE 5: Implementation Roadmap

### Step 5.1: Quick Wins (Low effort, high impact)
- [ ] Add candlestick chart option to Deep Scan
- [ ] Add Stock vs S&P 500 comparison to Command Deck
- [ ] Add PE/EPS historical chart to The Vault

### Step 5.2: Deep Analysis Integration
- [ ] Create "Deep Analysis" tab in The Vault
- [ ] Integrate Income/Balance/Cash flow analysis functions
- [ ] Add Risk Assessment section
- [ ] Add Competitor Analysis (if FMP API supports)

### Step 5.3: Backtest Arena (New Page)
- [ ] Create backtest configuration UI
- [ ] Strategy selector (SMA Crossover, etc.)
- [ ] Date range picker
- [ ] Results display (metrics + chart)

### Step 5.4: Report Forge (New Page)
- [ ] Multi-step wizard for report generation
- [ ] Preview sections before PDF generation
- [ ] Download PDF functionality

### Step 5.5: Advanced Oracle
- [ ] Agent type selector in The Oracle
- [ ] Specialized prompts per agent type
- [ ] RAG integration for document Q&A

---

## ✅ Testing Checklist

### Before Each Phase
- [ ] Verify API keys are configured
- [ ] Check API rate limits
- [ ] Ensure test data exists (stock tickers, date ranges)

### After Each Test
- [ ] Document what works ✓
- [ ] Document what fails ✗
- [ ] Note any API limitations
- [ ] Record performance (speed)

---

## 📋 API Requirements Summary

| API | Required For | Free Tier Limitations |
|-----|--------------|----------------------|
| OpenAI | AI analysis, RAG | Token limits |
| SEC API | 10-K sections | Rate limits |
| FMP | Competitor metrics, Target price | Many endpoints paid-only |
| YFinance | Stock data, financials | Free |
| Finnhub | Company profile, news | Rate limits |

---

## Next Steps

1. **Run Phase 1 tests** → Validate analysis functions work
2. **Review results** → Identify what needs fixing
3. **Proceed to Phase 2** → Test backtesting & charting
4. **Finalize UI plan** → Based on what actually works
5. **Implement incrementally** → One feature at a time

---

*Document created: January 3, 2026*
*Last updated: January 3, 2026*

