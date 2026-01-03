"""
Stock Comparison Utilities
Compare multiple stocks side-by-side on financials, valuations, and performance
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..data_source import YFinanceUtils, FMPUtils


class StockComparator:
    """Utility class for comparing multiple stocks"""
    
    @staticmethod
    def get_comparison_data(tickers: List[str]) -> Dict[str, Any]:
        """
        Get comprehensive comparison data for multiple stocks
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            Dictionary with comparison data for all stocks
        """
        results = {
            "tickers": tickers,
            "overview": {},
            "financials": {},
            "valuations": {},
            "growth": {},
            "performance": {},
            "errors": []
        }
        
        for ticker in tickers:
            try:
                # Get stock info
                info = YFinanceUtils.get_stock_info(ticker)
                
                if not info:
                    results["errors"].append(f"Could not fetch data for {ticker}")
                    continue
                
                # Overview data
                results["overview"][ticker] = {
                    "name": info.get("shortName", ticker),
                    "sector": info.get("sector", "N/A"),
                    "industry": info.get("industry", "N/A"),
                    "market_cap": info.get("marketCap", 0),
                    "employees": info.get("fullTimeEmployees", "N/A"),
                    "country": info.get("country", "N/A")
                }
                
                # Financial metrics
                results["financials"][ticker] = {
                    "revenue": info.get("totalRevenue", 0),
                    "net_income": info.get("netIncomeToCommon", 0),
                    "gross_profit": info.get("grossProfits", 0),
                    "ebitda": info.get("ebitda", 0),
                    "operating_income": info.get("operatingIncome", 0),
                    "free_cash_flow": info.get("freeCashflow", 0),
                    "total_cash": info.get("totalCash", 0),
                    "total_debt": info.get("totalDebt", 0),
                }
                
                # Calculate margins
                revenue = info.get("totalRevenue", 0) or 1  # Avoid division by zero
                results["financials"][ticker]["gross_margin"] = (
                    info.get("grossProfits", 0) / revenue * 100 if revenue else 0
                )
                results["financials"][ticker]["operating_margin"] = (
                    info.get("operatingMargins", 0) * 100 if info.get("operatingMargins") else 0
                )
                results["financials"][ticker]["net_margin"] = (
                    info.get("profitMargins", 0) * 100 if info.get("profitMargins") else 0
                )
                
                # Valuation metrics
                results["valuations"][ticker] = {
                    "pe_ratio": info.get("trailingPE", None),
                    "forward_pe": info.get("forwardPE", None),
                    "peg_ratio": info.get("pegRatio", None),
                    "ps_ratio": info.get("priceToSalesTrailing12Months", None),
                    "pb_ratio": info.get("priceToBook", None),
                    "ev_ebitda": info.get("enterpriseToEbitda", None),
                    "ev_revenue": info.get("enterpriseToRevenue", None),
                    "market_cap": info.get("marketCap", 0),
                    "enterprise_value": info.get("enterpriseValue", 0),
                }
                
                # Growth metrics
                results["growth"][ticker] = {
                    "revenue_growth": info.get("revenueGrowth", 0) * 100 if info.get("revenueGrowth") else 0,
                    "earnings_growth": info.get("earningsGrowth", 0) * 100 if info.get("earningsGrowth") else 0,
                    "quarterly_revenue_growth": info.get("revenueQuarterlyGrowth", 0) * 100 if info.get("revenueQuarterlyGrowth") else 0,
                    "quarterly_earnings_growth": info.get("earningsQuarterlyGrowth", 0) * 100 if info.get("earningsQuarterlyGrowth") else 0,
                }
                
            except Exception as e:
                results["errors"].append(f"Error fetching {ticker}: {str(e)}")
        
        return results
    
    @staticmethod
    def get_price_performance(tickers: List[str], period_days: int = 365) -> Dict[str, Any]:
        """
        Compare price performance across multiple stocks
        
        Args:
            tickers: List of stock ticker symbols
            period_days: Number of days to look back
            
        Returns:
            Dictionary with price performance data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        results = {
            "tickers": tickers,
            "period_days": period_days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "performance": {},
            "price_data": {},
            "normalized": {}
        }
        
        for ticker in tickers:
            try:
                # Get historical data
                data = YFinanceUtils.get_stock_data(
                    ticker,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                
                if data is not None and not data.empty:
                    # Calculate returns
                    start_price = data['Close'].iloc[0]
                    end_price = data['Close'].iloc[-1]
                    total_return = ((end_price - start_price) / start_price) * 100
                    
                    # Calculate volatility
                    daily_returns = data['Close'].pct_change().dropna()
                    volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized
                    
                    # Calculate max drawdown
                    cumulative = (1 + daily_returns).cumprod()
                    rolling_max = cumulative.cummax()
                    drawdown = (cumulative - rolling_max) / rolling_max
                    max_drawdown = drawdown.min() * 100
                    
                    results["performance"][ticker] = {
                        "total_return": round(total_return, 2),
                        "start_price": round(start_price, 2),
                        "end_price": round(end_price, 2),
                        "volatility": round(volatility, 2),
                        "max_drawdown": round(max_drawdown, 2),
                        "sharpe_ratio": round(total_return / volatility if volatility else 0, 2)
                    }
                    
                    # Store normalized data for charting
                    normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                    results["normalized"][ticker] = normalized.to_dict()
                    
            except Exception as e:
                results["performance"][ticker] = {"error": str(e)}
        
        # Add S&P 500 for comparison
        try:
            sp500_data = YFinanceUtils.get_stock_data(
                "^GSPC",
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            if sp500_data is not None and not sp500_data.empty:
                start_price = sp500_data['Close'].iloc[0]
                end_price = sp500_data['Close'].iloc[-1]
                sp500_return = ((end_price - start_price) / start_price) * 100
                results["performance"]["S&P 500"] = {
                    "total_return": round(sp500_return, 2),
                    "start_price": round(start_price, 2),
                    "end_price": round(end_price, 2)
                }
                normalized = (sp500_data['Close'] / sp500_data['Close'].iloc[0] - 1) * 100
                results["normalized"]["S&P 500"] = normalized.to_dict()
        except:
            pass
        
        return results
    
    @staticmethod
    def get_financial_history(tickers: List[str], years: int = 5) -> Dict[str, Any]:
        """
        Get historical financial data for comparison
        
        Args:
            tickers: List of stock ticker symbols
            years: Number of years of history
            
        Returns:
            Dictionary with historical financial data
        """
        results = {
            "tickers": tickers,
            "years": years,
            "revenue_history": {},
            "income_history": {},
            "eps_history": {},
            "errors": []
        }
        
        for ticker in tickers:
            try:
                # Get income statement
                income_stmt = YFinanceUtils.get_income_stmt(ticker)
                
                if income_stmt is not None and not income_stmt.empty:
                    # Get last N years of data
                    cols = income_stmt.columns[:years] if len(income_stmt.columns) >= years else income_stmt.columns
                    
                    # Revenue
                    if "Total Revenue" in income_stmt.index:
                        revenue = income_stmt.loc["Total Revenue", cols]
                        results["revenue_history"][ticker] = {
                            str(col.year) if hasattr(col, 'year') else str(col): float(val) if pd.notna(val) else 0 
                            for col, val in revenue.items()
                        }
                    
                    # Net Income
                    if "Net Income" in income_stmt.index:
                        net_income = income_stmt.loc["Net Income", cols]
                        results["income_history"][ticker] = {
                            str(col.year) if hasattr(col, 'year') else str(col): float(val) if pd.notna(val) else 0 
                            for col, val in net_income.items()
                        }
                    
                    # EPS
                    if "Diluted EPS" in income_stmt.index:
                        eps = income_stmt.loc["Diluted EPS", cols]
                        results["eps_history"][ticker] = {
                            str(col.year) if hasattr(col, 'year') else str(col): float(val) if pd.notna(val) else 0 
                            for col, val in eps.items()
                        }
                        
            except Exception as e:
                results["errors"].append(f"Error fetching history for {ticker}: {str(e)}")
        
        return results
    
    @staticmethod
    def create_comparison_table(tickers: List[str]) -> pd.DataFrame:
        """
        Create a formatted comparison table for multiple stocks
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            DataFrame with comparison data
        """
        data = StockComparator.get_comparison_data(tickers)
        
        # Build comparison table
        rows = []
        
        # Helper to format large numbers
        def format_num(val, is_currency=False, is_pct=False):
            if val is None or val == 0:
                return "N/A"
            if is_pct:
                return f"{val:.1f}%"
            if is_currency:
                if abs(val) >= 1e12:
                    return f"${val/1e12:.1f}T"
                elif abs(val) >= 1e9:
                    return f"${val/1e9:.1f}B"
                elif abs(val) >= 1e6:
                    return f"${val/1e6:.1f}M"
                else:
                    return f"${val:,.0f}"
            if abs(val) >= 1e12:
                return f"{val/1e12:.1f}T"
            elif abs(val) >= 1e9:
                return f"{val/1e9:.1f}B"
            elif abs(val) >= 1e6:
                return f"{val/1e6:.1f}M"
            return f"{val:.2f}"
        
        metrics = [
            ("Market Cap", "valuations", "market_cap", True, False),
            ("Revenue", "financials", "revenue", True, False),
            ("Net Income", "financials", "net_income", True, False),
            ("Gross Margin", "financials", "gross_margin", False, True),
            ("Operating Margin", "financials", "operating_margin", False, True),
            ("Net Margin", "financials", "net_margin", False, True),
            ("P/E Ratio", "valuations", "pe_ratio", False, False),
            ("Forward P/E", "valuations", "forward_pe", False, False),
            ("P/S Ratio", "valuations", "ps_ratio", False, False),
            ("P/B Ratio", "valuations", "pb_ratio", False, False),
            ("EV/EBITDA", "valuations", "ev_ebitda", False, False),
            ("PEG Ratio", "valuations", "peg_ratio", False, False),
            ("Revenue Growth", "growth", "revenue_growth", False, True),
            ("Earnings Growth", "growth", "earnings_growth", False, True),
        ]
        
        for metric_name, category, key, is_currency, is_pct in metrics:
            row = {"Metric": metric_name}
            for ticker in tickers:
                if ticker in data[category] and key in data[category][ticker]:
                    val = data[category][ticker][key]
                    row[ticker] = format_num(val, is_currency, is_pct)
                else:
                    row[ticker] = "N/A"
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.set_index("Metric", inplace=True)
        
        return df
    
    @staticmethod
    def identify_best_in_class(tickers: List[str]) -> Dict[str, str]:
        """
        Identify which stock is best for each metric
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            Dictionary mapping metrics to best performing stock
        """
        data = StockComparator.get_comparison_data(tickers)
        
        best = {}
        
        # Higher is better
        higher_better = [
            ("revenue", "financials", "Highest Revenue"),
            ("net_income", "financials", "Most Profitable"),
            ("gross_margin", "financials", "Best Gross Margin"),
            ("net_margin", "financials", "Best Net Margin"),
            ("revenue_growth", "growth", "Fastest Growing"),
        ]
        
        # Lower is better (for valuations, generally)
        lower_better = [
            ("pe_ratio", "valuations", "Cheapest P/E"),
            ("ps_ratio", "valuations", "Cheapest P/S"),
            ("ev_ebitda", "valuations", "Cheapest EV/EBITDA"),
        ]
        
        for key, category, label in higher_better:
            max_val = None
            max_ticker = None
            for ticker in tickers:
                if ticker in data[category] and key in data[category][ticker]:
                    val = data[category][ticker][key]
                    if val is not None and (max_val is None or val > max_val):
                        max_val = val
                        max_ticker = ticker
            if max_ticker:
                best[label] = max_ticker
        
        for key, category, label in lower_better:
            min_val = None
            min_ticker = None
            for ticker in tickers:
                if ticker in data[category] and key in data[category][ticker]:
                    val = data[category][ticker][key]
                    if val is not None and val > 0 and (min_val is None or val < min_val):
                        min_val = val
                        min_ticker = ticker
            if min_ticker:
                best[label] = min_ticker
        
        return best

