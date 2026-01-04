"""
Risk Analytics Module for Ikshvaku

Provides comprehensive risk analysis including:
- Value at Risk (VaR) - Historical and Parametric
- Sharpe Ratio and Sortino Ratio
- Maximum Drawdown Analysis
- Volatility (Historical and Rolling)
- Beta and Alpha
- Correlation Analysis
"""

from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from scipy import stats


class RiskAnalytics:
    """Comprehensive Risk Analysis Tools"""
    
    # Default assumptions
    TRADING_DAYS = 252
    RISK_FREE_RATE = 0.045  # 4.5% annual
    
    @staticmethod
    def get_returns(ticker: str, period: str = "1y") -> pd.Series:
        """
        Get daily returns for a stock.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1m, 3m, 6m, 1y, 2y, 5y)
            
        Returns:
            Series of daily returns
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return pd.Series()
            
            returns = hist['Close'].pct_change().dropna()
            return returns
            
        except Exception as e:
            return pd.Series()
    
    @staticmethod
    def calculate_var(
        ticker: str,
        confidence: float = 0.95,
        holding_period: int = 1,
        method: str = "historical",
        period: str = "1y"
    ) -> Dict[str, Any]:
        """
        Calculate Value at Risk (VaR).
        
        VaR represents the maximum expected loss at a given confidence level.
        
        Args:
            ticker: Stock ticker symbol
            confidence: Confidence level (0.95 = 95%, 0.99 = 99%)
            holding_period: Number of days to hold position
            method: "historical" or "parametric"
            period: Historical data period
            
        Returns:
            Dictionary with VaR metrics
        """
        try:
            returns = RiskAnalytics.get_returns(ticker, period)
            
            if returns.empty:
                return {"error": f"No data for {ticker}"}
            
            stock = yf.Ticker(ticker)
            current_price = stock.info.get("currentPrice") or stock.info.get("regularMarketPrice", 100)
            
            if method == "historical":
                # Historical VaR - use actual distribution
                var_pct = np.percentile(returns, (1 - confidence) * 100)
            else:
                # Parametric VaR - assume normal distribution
                mean = returns.mean()
                std = returns.std()
                z_score = stats.norm.ppf(1 - confidence)
                var_pct = mean + z_score * std
            
            # Adjust for holding period (square root of time)
            var_pct_adjusted = var_pct * np.sqrt(holding_period)
            
            # Dollar VaR per share
            var_dollar = current_price * abs(var_pct_adjusted)
            
            # Also calculate CVaR (Conditional VaR / Expected Shortfall)
            cvar_pct = returns[returns <= np.percentile(returns, (1 - confidence) * 100)].mean()
            cvar_dollar = current_price * abs(cvar_pct) * np.sqrt(holding_period)
            
            return {
                "ticker": ticker,
                "method": method,
                "confidence_level": confidence * 100,
                "holding_period_days": holding_period,
                "var_percent": round(abs(var_pct_adjusted) * 100, 2),
                "var_dollar_per_share": round(var_dollar, 2),
                "cvar_percent": round(abs(cvar_pct) * np.sqrt(holding_period) * 100, 2),
                "cvar_dollar_per_share": round(cvar_dollar, 2),
                "current_price": round(current_price, 2),
                "interpretation": f"With {confidence*100:.0f}% confidence, the maximum {holding_period}-day loss is ${var_dollar:.2f} per share ({abs(var_pct_adjusted)*100:.2f}%)"
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def calculate_sharpe_ratio(
        ticker: str,
        risk_free_rate: float = None,
        period: str = "1y"
    ) -> Dict[str, Any]:
        """
        Calculate Sharpe Ratio.
        
        Sharpe Ratio = (Return - Risk-Free Rate) / Standard Deviation
        
        Args:
            ticker: Stock ticker symbol
            risk_free_rate: Annual risk-free rate (default 4.5%)
            period: Historical data period
            
        Returns:
            Dictionary with Sharpe and related metrics
        """
        try:
            returns = RiskAnalytics.get_returns(ticker, period)
            
            if returns.empty:
                return {"error": f"No data for {ticker}"}
            
            rf = risk_free_rate or RiskAnalytics.RISK_FREE_RATE
            daily_rf = rf / RiskAnalytics.TRADING_DAYS
            
            # Annualized metrics
            annual_return = returns.mean() * RiskAnalytics.TRADING_DAYS
            annual_std = returns.std() * np.sqrt(RiskAnalytics.TRADING_DAYS)
            
            # Sharpe Ratio
            sharpe = (annual_return - rf) / annual_std if annual_std > 0 else 0
            
            # Sortino Ratio (only downside deviation)
            downside_returns = returns[returns < daily_rf]
            downside_std = downside_returns.std() * np.sqrt(RiskAnalytics.TRADING_DAYS)
            sortino = (annual_return - rf) / downside_std if downside_std > 0 else 0
            
            # Interpretation
            if sharpe >= 2:
                interpretation = "Excellent risk-adjusted returns"
            elif sharpe >= 1:
                interpretation = "Good risk-adjusted returns"
            elif sharpe >= 0.5:
                interpretation = "Moderate risk-adjusted returns"
            elif sharpe >= 0:
                interpretation = "Below average risk-adjusted returns"
            else:
                interpretation = "Poor risk-adjusted returns (underperforming risk-free rate)"
            
            return {
                "ticker": ticker,
                "period": period,
                "sharpe_ratio": round(sharpe, 2),
                "sortino_ratio": round(sortino, 2),
                "annual_return_percent": round(annual_return * 100, 2),
                "annual_volatility_percent": round(annual_std * 100, 2),
                "risk_free_rate_percent": round(rf * 100, 2),
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def calculate_max_drawdown(
        ticker: str,
        period: str = "1y"
    ) -> Dict[str, Any]:
        """
        Calculate Maximum Drawdown.
        
        Max Drawdown = largest peak-to-trough decline in portfolio value.
        
        Args:
            ticker: Stock ticker symbol
            period: Historical data period
            
        Returns:
            Dictionary with drawdown metrics
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return {"error": f"No data for {ticker}"}
            
            prices = hist['Close']
            
            # Calculate running maximum
            running_max = prices.cummax()
            
            # Calculate drawdown series
            drawdown = (prices - running_max) / running_max
            
            # Maximum drawdown
            max_dd = drawdown.min()
            max_dd_idx = drawdown.idxmin()
            
            # Find the peak before max drawdown
            peak_idx = prices[:max_dd_idx].idxmax()
            peak_price = prices[peak_idx]
            trough_price = prices[max_dd_idx]
            
            # Calculate recovery (if any)
            post_trough = prices[max_dd_idx:]
            recovered = (post_trough >= peak_price).any()
            if recovered:
                recovery_idx = post_trough[post_trough >= peak_price].index[0]
                recovery_days = (recovery_idx - max_dd_idx).days
            else:
                recovery_days = None
            
            # Current drawdown
            current_dd = drawdown.iloc[-1]
            
            # Average drawdown
            avg_dd = drawdown[drawdown < 0].mean()
            
            return {
                "ticker": ticker,
                "period": period,
                "max_drawdown_percent": round(abs(max_dd) * 100, 2),
                "max_drawdown_peak_date": peak_idx.strftime("%Y-%m-%d"),
                "max_drawdown_trough_date": max_dd_idx.strftime("%Y-%m-%d"),
                "peak_price": round(peak_price, 2),
                "trough_price": round(trough_price, 2),
                "recovered": recovered,
                "recovery_days": recovery_days,
                "current_drawdown_percent": round(abs(current_dd) * 100, 2),
                "average_drawdown_percent": round(abs(avg_dd) * 100, 2) if not np.isnan(avg_dd) else 0,
                "interpretation": f"Worst decline was {abs(max_dd)*100:.1f}% from peak of ${peak_price:.2f} to trough of ${trough_price:.2f}"
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def calculate_volatility(
        ticker: str,
        period: str = "1y",
        window: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate historical and rolling volatility.
        
        Args:
            ticker: Stock ticker symbol
            period: Historical data period
            window: Rolling window for volatility calculation
            
        Returns:
            Dictionary with volatility metrics
        """
        try:
            returns = RiskAnalytics.get_returns(ticker, period)
            
            if returns.empty:
                return {"error": f"No data for {ticker}"}
            
            # Historical volatility (annualized)
            hist_vol = returns.std() * np.sqrt(RiskAnalytics.TRADING_DAYS)
            
            # Rolling volatility
            rolling_vol = returns.rolling(window=window).std() * np.sqrt(RiskAnalytics.TRADING_DAYS)
            
            # Current rolling volatility
            current_rolling_vol = rolling_vol.iloc[-1]
            
            # Volatility percentiles
            vol_percentile = (rolling_vol < current_rolling_vol).mean() * 100
            
            # High/Low volatility in period
            max_vol = rolling_vol.max()
            min_vol = rolling_vol.min()
            avg_vol = rolling_vol.mean()
            
            # Interpretation
            if hist_vol > 0.50:
                risk_level = "Very High"
            elif hist_vol > 0.35:
                risk_level = "High"
            elif hist_vol > 0.20:
                risk_level = "Moderate"
            elif hist_vol > 0.10:
                risk_level = "Low"
            else:
                risk_level = "Very Low"
            
            return {
                "ticker": ticker,
                "period": period,
                "rolling_window_days": window,
                "historical_volatility_percent": round(hist_vol * 100, 2),
                "current_rolling_volatility_percent": round(current_rolling_vol * 100, 2),
                "volatility_percentile": round(vol_percentile, 1),
                "max_rolling_volatility_percent": round(max_vol * 100, 2),
                "min_rolling_volatility_percent": round(min_vol * 100, 2),
                "avg_rolling_volatility_percent": round(avg_vol * 100, 2),
                "risk_level": risk_level,
                "interpretation": f"Current volatility ({current_rolling_vol*100:.1f}%) is at the {vol_percentile:.0f}th percentile for the period"
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def calculate_beta_alpha(
        ticker: str,
        benchmark: str = "SPY",
        period: str = "1y"
    ) -> Dict[str, Any]:
        """
        Calculate Beta and Alpha relative to a benchmark.
        
        Beta = Covariance(stock, market) / Variance(market)
        Alpha = Stock Return - (Risk-Free Rate + Beta × (Market Return - Risk-Free Rate))
        
        Args:
            ticker: Stock ticker symbol
            benchmark: Benchmark ticker (default SPY)
            period: Historical data period
            
        Returns:
            Dictionary with beta and alpha metrics
        """
        try:
            stock_returns = RiskAnalytics.get_returns(ticker, period)
            market_returns = RiskAnalytics.get_returns(benchmark, period)
            
            if stock_returns.empty or market_returns.empty:
                return {"error": f"No data for {ticker} or {benchmark}"}
            
            # Align the data
            combined = pd.concat([stock_returns, market_returns], axis=1).dropna()
            combined.columns = ['stock', 'market']
            
            if len(combined) < 30:
                return {"error": "Insufficient data for beta calculation"}
            
            # Calculate Beta using linear regression
            covariance = combined['stock'].cov(combined['market'])
            market_variance = combined['market'].var()
            
            beta = covariance / market_variance if market_variance > 0 else 1
            
            # Calculate Alpha (Jensen's Alpha)
            rf = RiskAnalytics.RISK_FREE_RATE
            daily_rf = rf / RiskAnalytics.TRADING_DAYS
            
            stock_annual_return = combined['stock'].mean() * RiskAnalytics.TRADING_DAYS
            market_annual_return = combined['market'].mean() * RiskAnalytics.TRADING_DAYS
            
            # CAPM expected return
            expected_return = rf + beta * (market_annual_return - rf)
            
            # Alpha = Actual - Expected
            alpha = stock_annual_return - expected_return
            
            # Correlation
            correlation = combined['stock'].corr(combined['market'])
            
            # R-squared
            r_squared = correlation ** 2
            
            # Interpretation
            if beta > 1.5:
                beta_interp = "Highly aggressive - moves significantly more than market"
            elif beta > 1:
                beta_interp = "Aggressive - moves more than market"
            elif beta > 0.8:
                beta_interp = "Neutral - moves with market"
            elif beta > 0.5:
                beta_interp = "Defensive - moves less than market"
            else:
                beta_interp = "Very defensive - minimal market correlation"
            
            return {
                "ticker": ticker,
                "benchmark": benchmark,
                "period": period,
                "beta": round(beta, 2),
                "alpha_percent": round(alpha * 100, 2),
                "correlation": round(correlation, 2),
                "r_squared": round(r_squared, 2),
                "stock_annual_return_percent": round(stock_annual_return * 100, 2),
                "market_annual_return_percent": round(market_annual_return * 100, 2),
                "expected_return_percent": round(expected_return * 100, 2),
                "beta_interpretation": beta_interp,
                "alpha_interpretation": f"Stock {'outperformed' if alpha > 0 else 'underperformed'} CAPM expectation by {abs(alpha)*100:.1f}%"
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def correlation_matrix(
        tickers: List[str],
        period: str = "1y"
    ) -> Dict[str, Any]:
        """
        Calculate correlation matrix for multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols
            period: Historical data period
            
        Returns:
            Dictionary with correlation matrix
        """
        try:
            # Get returns for all tickers
            returns_dict = {}
            for ticker in tickers:
                returns = RiskAnalytics.get_returns(ticker, period)
                if not returns.empty:
                    returns_dict[ticker] = returns
            
            if len(returns_dict) < 2:
                return {"error": "Need at least 2 valid tickers for correlation"}
            
            # Create DataFrame
            returns_df = pd.DataFrame(returns_dict)
            
            # Calculate correlation matrix
            corr_matrix = returns_df.corr()
            
            # Find highest and lowest correlations (excluding diagonal)
            corr_values = []
            for i, ticker1 in enumerate(corr_matrix.columns):
                for j, ticker2 in enumerate(corr_matrix.columns):
                    if i < j:
                        corr_values.append({
                            "pair": f"{ticker1}-{ticker2}",
                            "correlation": round(corr_matrix.loc[ticker1, ticker2], 3)
                        })
            
            corr_values.sort(key=lambda x: x['correlation'], reverse=True)
            
            return {
                "tickers": list(returns_dict.keys()),
                "period": period,
                "matrix": corr_matrix.round(3).to_dict(),
                "highest_correlation": corr_values[0] if corr_values else None,
                "lowest_correlation": corr_values[-1] if corr_values else None,
                "all_pairs": corr_values
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_risk_summary(ticker: str, period: str = "1y") -> str:
        """
        Get a formatted risk summary for AI responses.
        
        Args:
            ticker: Stock ticker symbol
            period: Historical data period
            
        Returns:
            Formatted string summary
        """
        var = RiskAnalytics.calculate_var(ticker, period=period)
        sharpe = RiskAnalytics.calculate_sharpe_ratio(ticker, period=period)
        drawdown = RiskAnalytics.calculate_max_drawdown(ticker, period=period)
        volatility = RiskAnalytics.calculate_volatility(ticker, period=period)
        beta_alpha = RiskAnalytics.calculate_beta_alpha(ticker, period=period)
        
        if any("error" in x for x in [var, sharpe, drawdown, volatility, beta_alpha]):
            return f"Error calculating risk metrics for {ticker}"
        
        summary = f"""
RISK ANALYSIS FOR {ticker.upper()} ({period} period)
{'='*60}

📊 VALUE AT RISK (95% Confidence, 1-Day):
├── VaR: {var['var_percent']}% (${var['var_dollar_per_share']} per share)
├── CVaR (Expected Shortfall): {var['cvar_percent']}%
└── {var['interpretation']}

📈 RISK-ADJUSTED RETURNS:
├── Sharpe Ratio: {sharpe['sharpe_ratio']}
├── Sortino Ratio: {sharpe['sortino_ratio']}
├── Annual Return: {sharpe['annual_return_percent']}%
├── Annual Volatility: {sharpe['annual_volatility_percent']}%
└── {sharpe['interpretation']}

📉 MAXIMUM DRAWDOWN:
├── Max Drawdown: {drawdown['max_drawdown_percent']}%
├── Peak: ${drawdown['peak_price']} ({drawdown['max_drawdown_peak_date']})
├── Trough: ${drawdown['trough_price']} ({drawdown['max_drawdown_trough_date']})
├── Recovered: {'Yes' if drawdown['recovered'] else 'No'}
└── Current Drawdown: {drawdown['current_drawdown_percent']}%

🌊 VOLATILITY:
├── Historical (Annualized): {volatility['historical_volatility_percent']}%
├── Current Rolling ({volatility['rolling_window_days']}-day): {volatility['current_rolling_volatility_percent']}%
├── Volatility Percentile: {volatility['volatility_percentile']}th
└── Risk Level: {volatility['risk_level']}

🎯 BETA & ALPHA (vs {beta_alpha['benchmark']}):
├── Beta: {beta_alpha['beta']} ({beta_alpha['beta_interpretation']})
├── Alpha: {beta_alpha['alpha_percent']}%
├── Correlation: {beta_alpha['correlation']}
├── R-squared: {beta_alpha['r_squared']}
└── {beta_alpha['alpha_interpretation']}
"""
        return summary

