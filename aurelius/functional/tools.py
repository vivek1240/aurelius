"""
AI Command Center Tools
Defines all available tools for the AI agent to call
"""

import os
import json
import tempfile
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Import all utilities
from ..data_source import YFinanceUtils, FinnHubUtils, FMPUtils
from .charting import MplFinanceUtils, ReportChartUtils, ComparisonCharts
from .quantitative import BackTraderUtils
from .analyzer import ReportAnalysisUtils
from .strategies import STRATEGY_REGISTRY, STRATEGY_INFO
from .comparison import StockComparator


# ============================================================================
# TOOL DEFINITIONS (OpenAI Function Schemas)
# ============================================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get historical stock price data for a ticker symbol. Returns OHLCV data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, NVDA, MSFT)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of historical data (default 30)",
                        "default": 30
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_income_statement",
            "description": "Get the income statement (revenue, expenses, profit) for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_balance_sheet",
            "description": "Get the balance sheet (assets, liabilities, equity) for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cash_flow",
            "description": "Get the cash flow statement for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_profile",
            "description": "Get company profile information including industry, market cap, description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_news",
            "description": "Get recent news articles about a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back for news (default 7)",
                        "default": 7
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_price_chart",
            "description": "Create a stock price chart. Returns the chart as an image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["candle", "line", "ohlc", "renko", "pnf"],
                        "description": "Type of chart to create",
                        "default": "candle"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of data to show (default 90)",
                        "default": 90
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_comparison_chart",
            "description": "Create a chart comparing stock performance vs S&P 500 over the past year.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol to compare"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_backtest",
            "description": "Run a trading strategy backtest on historical data. Available strategies: SMA_CrossOver, RSI, MACD, BollingerBands, MA_Ribbon",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["SMA_CrossOver", "RSI", "MACD", "BollingerBands", "MA_Ribbon"],
                        "description": "Trading strategy to test"
                    },
                    "initial_capital": {
                        "type": "number",
                        "description": "Starting capital in USD (default 10000)",
                        "default": 10000
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of historical data (default 365)",
                        "default": 365
                    }
                },
                "required": ["ticker", "strategy"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_financials",
            "description": "Get AI-powered analysis of a company's financial statements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["income", "balance", "cashflow", "risk", "segment"],
                        "description": "Type of analysis to perform"
                    },
                    "fiscal_year": {
                        "type": "string",
                        "description": "Fiscal year (default current year)",
                        "default": "2024"
                    }
                },
                "required": ["ticker", "analysis_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_basic_financials",
            "description": "Get key financial metrics like P/E ratio, market cap, 52-week high/low.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_stocks",
            "description": "Compare multiple stocks side-by-side on financials, valuations, growth, and performance. Great for analyzing competitors or sector peers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock ticker symbols to compare (e.g., ['NVDA', 'AMD', 'INTC'])"
                    },
                    "include_chart": {
                        "type": "boolean",
                        "description": "Whether to generate a performance comparison chart (default true)",
                        "default": True
                    },
                    "period_days": {
                        "type": "integer",
                        "description": "Number of days for performance comparison (default 365)",
                        "default": 365
                    }
                },
                "required": ["tickers"]
            }
        }
    }
]


# ============================================================================
# TOOL EXECUTORS
# ============================================================================

class ToolExecutor:
    """Executes tools and returns results"""
    
    @staticmethod
    def execute(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result"""
        
        try:
            if tool_name == "get_stock_price":
                return ToolExecutor._get_stock_price(**arguments)
            elif tool_name == "get_income_statement":
                return ToolExecutor._get_income_statement(**arguments)
            elif tool_name == "get_balance_sheet":
                return ToolExecutor._get_balance_sheet(**arguments)
            elif tool_name == "get_cash_flow":
                return ToolExecutor._get_cash_flow(**arguments)
            elif tool_name == "get_company_profile":
                return ToolExecutor._get_company_profile(**arguments)
            elif tool_name == "get_company_news":
                return ToolExecutor._get_company_news(**arguments)
            elif tool_name == "create_price_chart":
                return ToolExecutor._create_price_chart(**arguments)
            elif tool_name == "create_comparison_chart":
                return ToolExecutor._create_comparison_chart(**arguments)
            elif tool_name == "run_backtest":
                return ToolExecutor._run_backtest(**arguments)
            elif tool_name == "analyze_financials":
                return ToolExecutor._analyze_financials(**arguments)
            elif tool_name == "get_basic_financials":
                return ToolExecutor._get_basic_financials(**arguments)
            elif tool_name == "compare_stocks":
                return ToolExecutor._compare_stocks(**arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _get_stock_price(ticker: str, days: int = 30) -> Dict[str, Any]:
        """Get stock price data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = YFinanceUtils.get_stock_data(
            ticker,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if data is None or data.empty:
            return {"error": f"No data found for {ticker}"}
        
        # Get summary stats
        current_price = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
        change_pct = ((current_price - prev_close) / prev_close) * 100
        high = data['High'].max()
        low = data['Low'].min()
        avg_volume = data['Volume'].mean()
        
        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "change_percent": round(change_pct, 2),
            "period_high": round(high, 2),
            "period_low": round(low, 2),
            "avg_volume": int(avg_volume),
            "data_points": len(data),
            "start_date": data.index[0].strftime("%Y-%m-%d"),
            "end_date": data.index[-1].strftime("%Y-%m-%d")
        }
    
    @staticmethod
    def _get_income_statement(ticker: str) -> Dict[str, Any]:
        """Get income statement"""
        data = YFinanceUtils.get_income_stmt(ticker)
        
        if data is None or data.empty:
            return {"error": f"No income statement data for {ticker}"}
        
        # Extract key metrics from most recent period
        latest = data.iloc[:, 0]
        
        result = {"ticker": ticker, "metrics": {}}
        key_items = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'EBITDA']
        
        for item in key_items:
            if item in latest.index:
                value = latest[item]
                if value and not pd.isna(value):
                    result["metrics"][item] = f"${value/1e9:.2f}B" if abs(value) >= 1e9 else f"${value/1e6:.2f}M"
        
        return result
    
    @staticmethod
    def _get_balance_sheet(ticker: str) -> Dict[str, Any]:
        """Get balance sheet"""
        data = YFinanceUtils.get_balance_sheet(ticker)
        
        if data is None or data.empty:
            return {"error": f"No balance sheet data for {ticker}"}
        
        latest = data.iloc[:, 0]
        result = {"ticker": ticker, "metrics": {}}
        key_items = ['Total Assets', 'Total Liabilities Net Minority Interest', 'Total Equity Gross Minority Interest', 'Cash And Cash Equivalents']
        
        for item in key_items:
            if item in latest.index:
                value = latest[item]
                if value and not pd.isna(value):
                    result["metrics"][item] = f"${value/1e9:.2f}B" if abs(value) >= 1e9 else f"${value/1e6:.2f}M"
        
        return result
    
    @staticmethod
    def _get_cash_flow(ticker: str) -> Dict[str, Any]:
        """Get cash flow statement"""
        data = YFinanceUtils.get_cash_flow(ticker)
        
        if data is None or data.empty:
            return {"error": f"No cash flow data for {ticker}"}
        
        latest = data.iloc[:, 0]
        result = {"ticker": ticker, "metrics": {}}
        key_items = ['Operating Cash Flow', 'Free Cash Flow', 'Capital Expenditure']
        
        for item in key_items:
            if item in latest.index:
                value = latest[item]
                if value and not pd.isna(value):
                    result["metrics"][item] = f"${value/1e9:.2f}B" if abs(value) >= 1e9 else f"${value/1e6:.2f}M"
        
        return result
    
    @staticmethod
    def _get_company_profile(ticker: str) -> Dict[str, Any]:
        """Get company profile"""
        try:
            profile = FinnHubUtils.get_company_profile(ticker)
            if profile:
                return {"ticker": ticker, "profile": profile}
        except:
            pass
        
        # Fallback to yfinance
        try:
            info = YFinanceUtils.get_stock_info(ticker)
            return {
                "ticker": ticker,
                "profile": {
                    "name": info.get('shortName', ticker),
                    "industry": info.get('industry', 'N/A'),
                    "sector": info.get('sector', 'N/A'),
                    "market_cap": info.get('marketCap', 'N/A'),
                    "employees": info.get('fullTimeEmployees', 'N/A')
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _get_company_news(ticker: str, days: int = 7) -> Dict[str, Any]:
        """Get company news"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            news_df = FinnHubUtils.get_company_news(
                ticker,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                max_news_num=5
            )
            
            if news_df is not None and not news_df.empty:
                news_items = []
                for _, row in news_df.iterrows():
                    news_items.append({
                        "headline": row.get('headline', 'No headline'),
                        "summary": row.get('summary', '')[:200]
                    })
                return {"ticker": ticker, "news": news_items}
            
            return {"ticker": ticker, "news": [], "message": "No recent news found"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _create_price_chart(ticker: str, chart_type: str = "candle", days: int = 90) -> Dict[str, Any]:
        """Create a price chart and return as base64 image"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Create temp file for chart
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            MplFinanceUtils.plot_stock_price_chart(
                ticker_symbol=ticker,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                save_path=tmp_path,
                type=chart_type,
                style="nightclouds"
            )
            
            # Read and encode image
            with open(tmp_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            
            # Cleanup
            os.unlink(tmp_path)
            
            return {
                "ticker": ticker,
                "chart_type": chart_type,
                "image_base64": img_data,
                "has_image": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _create_comparison_chart(ticker: str) -> Dict[str, Any]:
        """Create stock vs S&P 500 comparison chart"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            ReportChartUtils.get_share_performance(
                ticker,
                datetime.now().strftime("%Y-%m-%d"),
                tmp_path
            )
            
            with open(tmp_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            
            os.unlink(tmp_path)
            
            return {
                "ticker": ticker,
                "comparison": "vs S&P 500",
                "image_base64": img_data,
                "has_image": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _run_backtest(ticker: str, strategy: str, initial_capital: float = 10000, days: int = 365) -> Dict[str, Any]:
        """Run a backtest"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get strategy string
            strategy_string = STRATEGY_REGISTRY.get(strategy, strategy)
            
            # Default params per strategy
            params = {}
            if strategy == "SMA_CrossOver":
                params = {"fast": 10, "slow": 30}
            elif strategy == "RSI":
                params = {"period": 14, "oversold": 30, "overbought": 70}
            elif strategy == "MACD":
                params = {"fast_period": 12, "slow_period": 26, "signal_period": 9}
            elif strategy == "BollingerBands":
                params = {"period": 20, "devfactor": 2.0}
            
            result = BackTraderUtils.back_test(
                ticker,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                strategy=strategy_string,
                strategy_params=json.dumps(params) if params else '',
                cash=initial_capital
            )
            
            # Parse result
            import re
            final_match = re.search(r"'Final Portfolio Value': ([\d.]+)", result)
            final_value = float(final_match.group(1)) if final_match else initial_capital
            
            return {
                "ticker": ticker,
                "strategy": strategy,
                "initial_capital": initial_capital,
                "final_value": round(final_value, 2),
                "return_percent": round(((final_value - initial_capital) / initial_capital) * 100, 2),
                "profit_loss": round(final_value - initial_capital, 2)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _analyze_financials(ticker: str, analysis_type: str, fiscal_year: str = "2024") -> Dict[str, Any]:
        """Run financial analysis"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as tmp:
                tmp_path = tmp.name
            
            if analysis_type == "income":
                ReportAnalysisUtils.analyze_income_stmt(ticker, fiscal_year, tmp_path)
            elif analysis_type == "balance":
                ReportAnalysisUtils.analyze_balance_sheet(ticker, fiscal_year, tmp_path)
            elif analysis_type == "cashflow":
                ReportAnalysisUtils.analyze_cash_flow(ticker, fiscal_year, tmp_path)
            elif analysis_type == "risk":
                ReportAnalysisUtils.get_risk_assessment(ticker, fiscal_year, tmp_path)
            elif analysis_type == "segment":
                ReportAnalysisUtils.analyze_segment_stmt(ticker, fiscal_year, tmp_path)
            
            with open(tmp_path, 'r') as f:
                content = f.read()
            
            os.unlink(tmp_path)
            
            return {
                "ticker": ticker,
                "analysis_type": analysis_type,
                "content": content[:2000]  # Limit length
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _get_basic_financials(ticker: str) -> Dict[str, Any]:
        """Get basic financial metrics"""
        try:
            financials = FinnHubUtils.get_basic_financials(ticker)
            if financials:
                return {"ticker": ticker, "financials": financials}
            return {"ticker": ticker, "financials": {}, "message": "Limited data available"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _compare_stocks(tickers: list, include_chart: bool = True, period_days: int = 365) -> Dict[str, Any]:
        """Compare multiple stocks side-by-side"""
        try:
            # Get comparison data
            comparison_data = StockComparator.get_comparison_data(tickers)
            performance_data = StockComparator.get_price_performance(tickers, period_days)
            best_in_class = StockComparator.identify_best_in_class(tickers)
            
            # Format the comparison table
            comparison_table = StockComparator.create_comparison_table(tickers)
            
            # Build result
            result = {
                "tickers": tickers,
                "comparison_table": comparison_table.to_dict(),
                "performance": performance_data.get("performance", {}),
                "best_in_class": best_in_class,
                "overview": comparison_data.get("overview", {}),
            }
            
            # Generate chart if requested
            if include_chart:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp_path = tmp.name
                
                ComparisonCharts.performance_comparison_chart(tickers, period_days, tmp_path)
                
                with open(tmp_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                
                os.unlink(tmp_path)
                
                result["image_base64"] = img_data
                result["has_image"] = True
            
            return result
            
        except Exception as e:
            return {"error": str(e)}


# Need pandas for some operations
import pandas as pd

