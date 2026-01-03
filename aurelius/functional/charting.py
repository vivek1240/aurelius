import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless operation
import mplfinance as mpf
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from typing import Annotated, List, Tuple
from pandas import DateOffset
from datetime import datetime, timedelta

from ..data_source.yfinance_utils import YFinanceUtils


class MplFinanceUtils:

    @staticmethod
    def plot_stock_price_chart(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"
        ],
        start_date: Annotated[
            str, "Start date of the historical data in 'YYYY-MM-DD' format"
        ],
        end_date: Annotated[
            str, "End date of the historical data in 'YYYY-MM-DD' format"
        ],
        save_path: Annotated[str, "File path where the plot should be saved"],
        verbose: Annotated[
            str, "Whether to print stock data to console. Default to False."
        ] = False,
        type: Annotated[
            str,
            "Type of the plot, should be one of 'candle','ohlc','line','renko','pnf','hollow_and_filled'. Default to 'candle'",
        ] = "candle",
        style: Annotated[
            str,
            "Style of the plot, should be one of 'default','classic','charles','yahoo','nightclouds','sas','blueskies','mike'. Default to 'default'.",
        ] = "default",
        mav: Annotated[
            int | List[int] | Tuple[int, ...] | None,
            "Moving average window(s) to plot on the chart. Default to None.",
        ] = None,
        show_nontrading: Annotated[
            bool, "Whether to show non-trading days on the chart. Default to False."
        ] = False,
    ) -> str:
        """
        Plot a stock price chart using mplfinance for the specified stock and time period,
        and save the plot to a file.
        """
        # Fetch historical data
        stock_data = YFinanceUtils.get_stock_data(ticker_symbol, start_date, end_date)
        if verbose:
            print(stock_data.to_string())

        params = {
            "type": type,
            "style": style,
            "title": f"{ticker_symbol} {type} chart",
            "ylabel": "Price",
            "volume": True,
            "ylabel_lower": "Volume",
            "mav": mav,
            "show_nontrading": show_nontrading,
            "savefig": save_path,
        }
        # Using dictionary comprehension to filter out None values (MplFinance does not accept None values)
        filtered_params = {k: v for k, v in params.items() if v is not None}

        # Plot chart
        mpf.plot(stock_data, **filtered_params)

        return f"{type} chart saved to <img {save_path}>"


class ReportChartUtils:

    @staticmethod
    def get_share_performance(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"
        ],
        filing_date: Annotated[str | datetime, "filing date in 'YYYY-MM-DD' format"],
        save_path: Annotated[str, "File path where the plot should be saved"],
    ) -> str:
        """Plot the stock performance of a company compared to the S&P 500 over the past year."""
        if isinstance(filing_date, str):
            filing_date = datetime.strptime(filing_date, "%Y-%m-%d")

        def fetch_stock_data(ticker):
            start = (filing_date - timedelta(days=365)).strftime("%Y-%m-%d")
            end = filing_date.strftime("%Y-%m-%d")
            historical_data = YFinanceUtils.get_stock_data(ticker, start, end)
            # hist = stock.history(period=period)
            return historical_data["Close"]

        target_close = fetch_stock_data(ticker_symbol)
        sp500_close = fetch_stock_data("^GSPC")
        info = YFinanceUtils.get_stock_info(ticker_symbol)

        # 计算变化率
        company_change = (
            (target_close - target_close.iloc[0]) / target_close.iloc[0] * 100
        )
        sp500_change = (sp500_close - sp500_close.iloc[0]) / sp500_close.iloc[0] * 100

        # 计算额外的日期点
        start_date = company_change.index.min()
        four_months = start_date + DateOffset(months=4)
        eight_months = start_date + DateOffset(months=8)
        end_date = company_change.index.max()

        # 准备绘图
        plt.rcParams.update({"font.size": 20})  # 调整为更大的字体大小
        plt.figure(figsize=(14, 7))
        plt.plot(
            company_change.index,
            company_change,
            label=f'{info["shortName"]} Change %',
            color="blue",
        )
        plt.plot(
            sp500_change.index, sp500_change, label="S&P 500 Change %", color="red"
        )

        # 设置标题和标签
        plt.title(f'{info["shortName"]} vs S&P 500 - Change % Over the Past Year')
        plt.xlabel("Date")
        plt.ylabel("Change %")

        # 设置x轴刻度标签
        plt.xticks(
            [start_date, four_months, eight_months, end_date],
            [
                start_date.strftime("%Y-%m"),
                four_months.strftime("%Y-%m"),
                eight_months.strftime("%Y-%m"),
                end_date.strftime("%Y-%m"),
            ],
        )

        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        # plt.show()
        plot_path = (
            f"{save_path}/stock_performance.png"
            if os.path.isdir(save_path)
            else save_path
        )
        plt.savefig(plot_path)
        plt.close()
        return f"last year stock performance chart saved to <img {plot_path}>"

    @staticmethod
    def get_pe_eps_performance(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"
        ],
        filing_date: Annotated[str | datetime, "filing date in 'YYYY-MM-DD' format"],
        years: Annotated[int, "number of years to search from, default to 4"] = 4,
        save_path: Annotated[str, "File path where the plot should be saved"] = None,
    ) -> str:
        """Plot the PE ratio and EPS performance of a company over the past n years."""
        if isinstance(filing_date, str):
            filing_date = datetime.strptime(filing_date, "%Y-%m-%d")

        ss = YFinanceUtils.get_income_stmt(ticker_symbol)
        eps = ss.loc["Diluted EPS", :]

        # 获取过去5年的历史数据
        # historical_data = self.stock.history(period="5y")
        days = round((years + 1) * 365.25)
        start = (filing_date - timedelta(days=days)).strftime("%Y-%m-%d")
        end = filing_date.strftime("%Y-%m-%d")
        historical_data = YFinanceUtils.get_stock_data(ticker_symbol, start, end)

        # 指定的日期，并确保它们都是UTC时区的
        dates = pd.to_datetime(eps.index[::-1], utc=True)

        # 为了确保我们能够找到最接近的股市交易日，我们将转换日期并查找最接近的日期
        results = {}
        for date in dates:
            # 如果指定日期不是交易日，使用bfill和ffill找到最近的交易日股价
            if date not in historical_data.index:
                close_price = historical_data.asof(date)
            else:
                close_price = historical_data.loc[date]

            results[date] = close_price["Close"]

        pe = [p / e for p, e in zip(results.values(), eps.values[::-1])]
        dates = eps.index[::-1]
        eps = eps.values[::-1]

        info = YFinanceUtils.get_stock_info(ticker_symbol)

        # 创建图形和轴对象
        fig, ax1 = plt.subplots(figsize=(14, 7))
        plt.rcParams.update({"font.size": 20})  # 调整为更大的字体大小

        # 绘制市盈率
        color = "tab:blue"
        ax1.set_xlabel("Date")
        ax1.set_ylabel("PE Ratio", color=color)
        ax1.plot(dates, pe, color=color)
        ax1.tick_params(axis="y", labelcolor=color)
        ax1.grid(True)

        # 创建与ax1共享x轴的第二个轴对象
        ax2 = ax1.twinx()
        color = "tab:red"
        ax2.set_ylabel("EPS", color=color)  # 第二个y轴的标签
        ax2.plot(dates, eps, color=color)
        ax2.tick_params(axis="y", labelcolor=color)

        # 设置标题和x轴标签角度
        plt.title(f'{info["shortName"]} PE Ratios and EPS Over the Past {years} Years')
        plt.xticks(rotation=45)

        # 设置x轴刻度标签
        plt.xticks(dates, [d.strftime("%Y-%m") for d in dates])

        plt.tight_layout()
        # plt.show()
        plot_path = (
            f"{save_path}/pe_performance.png" if os.path.isdir(save_path) else save_path
        )
        plt.savefig(plot_path)
        plt.close()
        return f"pe performance chart saved to <img {plot_path}>"


class ComparisonCharts:
    """Charts for comparing multiple stocks"""
    
    @staticmethod
    def performance_comparison_chart(
        tickers: list,
        period_days: int = 365,
        save_path: str = None
    ) -> str:
        """
        Create a normalized price performance comparison chart
        
        Args:
            tickers: List of ticker symbols to compare
            period_days: Number of days to look back
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .comparison import StockComparator
        
        # Get performance data
        perf_data = StockComparator.get_price_performance(tickers, period_days)
        
        # Setup plot
        plt.rcParams.update({"font.size": 12})
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Colors for different stocks
        colors = ['#d4af37', '#00c896', '#ff4757', '#6366f1', '#a855f7', '#f97316']
        
        # Plot each stock
        for i, ticker in enumerate(tickers + (["S&P 500"] if "S&P 500" in perf_data["normalized"] else [])):
            if ticker in perf_data["normalized"]:
                data = perf_data["normalized"][ticker]
                dates = pd.to_datetime(list(data.keys()))
                values = list(data.values())
                color = colors[i % len(colors)]
                linewidth = 2.5 if ticker != "S&P 500" else 1.5
                linestyle = '-' if ticker != "S&P 500" else '--'
                ax.plot(dates, values, label=ticker, color=color, linewidth=linewidth, linestyle=linestyle)
        
        # Styling
        ax.axhline(y=0, color='white', linestyle='-', linewidth=0.5, alpha=0.3)
        ax.set_facecolor('#0d0d12')
        fig.patch.set_facecolor('#0d0d12')
        
        ax.set_title(f"Stock Performance Comparison ({period_days} Days)", 
                     fontsize=16, color='white', fontweight='bold', pad=20)
        ax.set_xlabel("Date", color='#a0a0a8', fontsize=12)
        ax.set_ylabel("Return (%)", color='#a0a0a8', fontsize=12)
        
        ax.tick_params(colors='#a0a0a8')
        ax.spines['bottom'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#333')
        ax.grid(True, alpha=0.1, color='white')
        
        ax.legend(loc='upper left', facecolor='#1a1a24', edgecolor='#333', 
                  labelcolor='white', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Performance comparison chart saved to <img {save_path}>"
    
    @staticmethod
    def revenue_comparison_chart(
        tickers: list,
        years: int = 5,
        save_path: str = None
    ) -> str:
        """
        Create a grouped bar chart comparing revenue over time
        
        Args:
            tickers: List of ticker symbols
            years: Number of years of history
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .comparison import StockComparator
        
        # Get historical data
        hist_data = StockComparator.get_financial_history(tickers, years)
        
        # Setup plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Get all years
        all_years = set()
        for ticker in tickers:
            if ticker in hist_data["revenue_history"]:
                all_years.update(hist_data["revenue_history"][ticker].keys())
        years_list = sorted(all_years, reverse=True)[:years]
        years_list = sorted(years_list)
        
        # Bar positioning
        x = np.arange(len(years_list))
        width = 0.8 / len(tickers)
        colors = ['#d4af37', '#00c896', '#ff4757', '#6366f1', '#a855f7']
        
        # Plot bars for each ticker
        for i, ticker in enumerate(tickers):
            if ticker in hist_data["revenue_history"]:
                values = [hist_data["revenue_history"][ticker].get(year, 0) / 1e9 
                          for year in years_list]
                offset = (i - len(tickers)/2 + 0.5) * width
                ax.bar(x + offset, values, width, label=ticker, color=colors[i % len(colors)])
        
        # Styling
        ax.set_facecolor('#0d0d12')
        fig.patch.set_facecolor('#0d0d12')
        
        ax.set_title("Revenue Comparison (Billions $)", 
                     fontsize=16, color='white', fontweight='bold', pad=20)
        ax.set_xlabel("Year", color='#a0a0a8', fontsize=12)
        ax.set_ylabel("Revenue ($B)", color='#a0a0a8', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(years_list)
        
        ax.tick_params(colors='#a0a0a8')
        ax.spines['bottom'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#333')
        ax.grid(True, alpha=0.1, color='white', axis='y')
        
        ax.legend(loc='upper left', facecolor='#1a1a24', edgecolor='#333', 
                  labelcolor='white', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Revenue comparison chart saved to <img {save_path}>"
    
    @staticmethod
    def margins_comparison_chart(
        tickers: list,
        save_path: str = None
    ) -> str:
        """
        Create a grouped bar chart comparing margins
        
        Args:
            tickers: List of ticker symbols
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .comparison import StockComparator
        
        # Get comparison data
        data = StockComparator.get_comparison_data(tickers)
        
        # Setup plot
        fig, ax = plt.subplots(figsize=(12, 7))
        
        margin_types = ['Gross Margin', 'Operating Margin', 'Net Margin']
        x = np.arange(len(margin_types))
        width = 0.8 / len(tickers)
        colors = ['#d4af37', '#00c896', '#ff4757', '#6366f1', '#a855f7']
        
        # Plot bars for each ticker
        for i, ticker in enumerate(tickers):
            if ticker in data["financials"]:
                values = [
                    data["financials"][ticker].get("gross_margin", 0),
                    data["financials"][ticker].get("operating_margin", 0),
                    data["financials"][ticker].get("net_margin", 0)
                ]
                offset = (i - len(tickers)/2 + 0.5) * width
                ax.bar(x + offset, values, width, label=ticker, color=colors[i % len(colors)])
        
        # Styling
        ax.set_facecolor('#0d0d12')
        fig.patch.set_facecolor('#0d0d12')
        
        ax.set_title("Profit Margins Comparison (%)", 
                     fontsize=16, color='white', fontweight='bold', pad=20)
        ax.set_ylabel("Margin (%)", color='#a0a0a8', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(margin_types)
        
        ax.tick_params(colors='#a0a0a8')
        ax.spines['bottom'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#333')
        ax.grid(True, alpha=0.1, color='white', axis='y')
        
        ax.legend(loc='upper right', facecolor='#1a1a24', edgecolor='#333', 
                  labelcolor='white', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Margins comparison chart saved to <img {save_path}>"
    
    @staticmethod
    def valuation_comparison_chart(
        tickers: list,
        save_path: str = None
    ) -> str:
        """
        Create a valuation comparison chart (P/E, P/S, EV/EBITDA)
        
        Args:
            tickers: List of ticker symbols
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .comparison import StockComparator
        
        # Get comparison data
        data = StockComparator.get_comparison_data(tickers)
        
        # Setup plot
        fig, axes = plt.subplots(1, 3, figsize=(15, 6))
        fig.patch.set_facecolor('#0d0d12')
        
        colors = ['#d4af37', '#00c896', '#ff4757', '#6366f1', '#a855f7']
        
        metrics = [
            ('pe_ratio', 'P/E Ratio'),
            ('ps_ratio', 'P/S Ratio'),
            ('ev_ebitda', 'EV/EBITDA')
        ]
        
        for idx, (metric, title) in enumerate(metrics):
            ax = axes[idx]
            ax.set_facecolor('#0d0d12')
            
            values = []
            labels = []
            bar_colors = []
            
            for i, ticker in enumerate(tickers):
                if ticker in data["valuations"]:
                    val = data["valuations"][ticker].get(metric)
                    if val is not None and val > 0:
                        values.append(val)
                        labels.append(ticker)
                        bar_colors.append(colors[i % len(colors)])
            
            if values:
                bars = ax.bar(labels, values, color=bar_colors)
                
                # Add value labels on bars
                for bar, val in zip(bars, values):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                            f'{val:.1f}', ha='center', va='bottom', 
                            color='white', fontsize=10)
            
            ax.set_title(title, fontsize=14, color='white', fontweight='bold')
            ax.tick_params(colors='#a0a0a8')
            ax.spines['bottom'].set_color('#333')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#333')
            ax.grid(True, alpha=0.1, color='white', axis='y')
        
        plt.suptitle("Valuation Multiples Comparison", 
                     fontsize=16, color='white', fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Valuation comparison chart saved to <img {save_path}>"


class EarningsCharts:
    """Charts for earnings intelligence visualization"""
    
    @staticmethod
    def eps_surprise_chart(
        ticker: str,
        quarters: int = 8,
        save_path: str = None
    ) -> str:
        """
        Create EPS actual vs estimate chart with surprise indicators
        
        Args:
            ticker: Stock ticker symbol
            quarters: Number of quarters to show
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .earnings import EarningsIntel
        
        # Get earnings data
        earnings_data = EarningsIntel.get_earnings_history(ticker, quarters)
        
        if not earnings_data.get("quarters"):
            return "No earnings data available"
        
        # Prepare data
        dates = []
        eps_estimates = []
        eps_actuals = []
        surprises = []
        
        for q in reversed(earnings_data["quarters"]):  # Oldest to newest
            dates.append(q["date"][:7])  # YYYY-MM format
            eps_estimates.append(q["eps_estimate"] or 0)
            eps_actuals.append(q["eps_actual"] or 0)
            surprises.append(q["surprise_pct"] or 0)
        
        # Setup plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1]})
        fig.patch.set_facecolor('#0d0d12')
        
        x = np.arange(len(dates))
        width = 0.35
        
        # Top chart: EPS Actual vs Estimate
        ax1.set_facecolor('#0d0d12')
        bars1 = ax1.bar(x - width/2, eps_estimates, width, label='EPS Estimate', color='#6366f1', alpha=0.8)
        bars2 = ax1.bar(x + width/2, eps_actuals, width, label='EPS Actual', color='#d4af37', alpha=0.9)
        
        ax1.set_title(f'{ticker} - EPS: Actual vs Estimate', fontsize=16, color='white', fontweight='bold', pad=20)
        ax1.set_ylabel('EPS ($)', color='#a0a0a8', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates, rotation=45, ha='right')
        ax1.tick_params(colors='#a0a0a8')
        ax1.spines['bottom'].set_color('#333')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#333')
        ax1.grid(True, alpha=0.1, color='white', axis='y')
        ax1.legend(loc='upper left', facecolor='#1a1a24', edgecolor='#333', labelcolor='white')
        
        # Bottom chart: Surprise %
        ax2.set_facecolor('#0d0d12')
        colors = ['#00c896' if s >= 0 else '#ff4757' for s in surprises]
        bars3 = ax2.bar(x, surprises, color=colors, alpha=0.8)
        
        # Add value labels on bars
        for bar, val in zip(bars3, surprises):
            height = bar.get_height()
            ax2.annotate(f'{val:+.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -12),
                        textcoords="offset points",
                        ha='center', va='bottom' if height >= 0 else 'top',
                        color='white', fontsize=9)
        
        ax2.axhline(y=0, color='white', linestyle='-', linewidth=0.5, alpha=0.3)
        ax2.set_title('Earnings Surprise (%)', fontsize=14, color='white', fontweight='bold', pad=10)
        ax2.set_ylabel('Surprise %', color='#a0a0a8', fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels(dates, rotation=45, ha='right')
        ax2.tick_params(colors='#a0a0a8')
        ax2.spines['bottom'].set_color('#333')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#333')
        ax2.grid(True, alpha=0.1, color='white', axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"EPS surprise chart saved to <img {save_path}>"
    
    @staticmethod
    def revenue_trend_chart(
        ticker: str,
        quarters: int = 8,
        save_path: str = None
    ) -> str:
        """
        Create revenue trend chart with YoY growth
        
        Args:
            ticker: Stock ticker symbol
            quarters: Number of quarters
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .earnings import EarningsIntel
        
        # Get revenue data
        revenue_data = EarningsIntel.get_revenue_history(ticker, quarters)
        
        if not revenue_data.get("quarters"):
            return "No revenue data available"
        
        # Prepare data
        dates = []
        revenues = []
        growths = []
        
        for q in reversed(revenue_data["quarters"]):
            dates.append(q["date"][:7])
            revenues.append((q["revenue"] or 0) / 1e9)  # Convert to billions
            growths.append(q["yoy_growth"] or 0)
        
        # Setup plot
        fig, ax1 = plt.subplots(figsize=(14, 7))
        fig.patch.set_facecolor('#0d0d12')
        ax1.set_facecolor('#0d0d12')
        
        x = np.arange(len(dates))
        
        # Bar chart for revenue
        bars = ax1.bar(x, revenues, color='#d4af37', alpha=0.8, label='Revenue')
        ax1.set_xlabel('Quarter', color='#a0a0a8', fontsize=12)
        ax1.set_ylabel('Revenue ($B)', color='#d4af37', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='#d4af37')
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates, rotation=45, ha='right')
        ax1.tick_params(colors='#a0a0a8')
        
        # Line chart for YoY growth on secondary axis
        ax2 = ax1.twinx()
        ax2.set_facecolor('#0d0d12')
        line = ax2.plot(x, growths, color='#00c896', linewidth=2.5, marker='o', 
                        markersize=8, label='YoY Growth %')
        ax2.set_ylabel('YoY Growth (%)', color='#00c896', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='#00c896')
        ax2.axhline(y=0, color='white', linestyle='--', linewidth=0.5, alpha=0.3)
        
        # Styling
        ax1.spines['bottom'].set_color('#333')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#333')
        ax2.spines['right'].set_color('#333')
        ax1.grid(True, alpha=0.1, color='white', axis='y')
        
        ax1.set_title(f'{ticker} - Quarterly Revenue & YoY Growth', 
                      fontsize=16, color='white', fontweight='bold', pad=20)
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
                   facecolor='#1a1a24', edgecolor='#333', labelcolor='white')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Revenue trend chart saved to <img {save_path}>"
    
    @staticmethod
    def analyst_estimates_chart(
        ticker: str,
        save_path: str = None
    ) -> str:
        """
        Create analyst price target visualization
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .earnings import EarningsIntel
        
        # Get analyst data
        analyst_data = EarningsIntel.get_analyst_estimates(ticker)
        
        if not analyst_data.get("price_targets"):
            return "No analyst data available"
        
        pt = analyst_data["price_targets"]
        current = pt.get("current_price", 0)
        target_low = pt.get("target_low", 0)
        target_mean = pt.get("target_mean", 0)
        target_high = pt.get("target_high", 0)
        
        if not all([current, target_low, target_mean, target_high]):
            return "Incomplete analyst data"
        
        # Setup plot
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#0d0d12')
        ax.set_facecolor('#0d0d12')
        
        # Create horizontal bar showing range
        y_pos = 0.5
        
        # Price range bar
        ax.barh(y_pos, target_high - target_low, left=target_low, height=0.3, 
                color='#2d2d3a', alpha=0.8)
        
        # Markers
        ax.plot(current, y_pos, 'o', markersize=20, color='#d4af37', label='Current Price', zorder=5)
        ax.plot(target_low, y_pos, '|', markersize=30, color='#ff4757', markeredgewidth=3, label='Target Low')
        ax.plot(target_mean, y_pos, 's', markersize=15, color='#00c896', label='Target Mean', zorder=5)
        ax.plot(target_high, y_pos, '|', markersize=30, color='#6366f1', markeredgewidth=3, label='Target High')
        
        # Add labels
        ax.annotate(f'${current:.2f}\n(Current)', (current, y_pos + 0.25), 
                    ha='center', va='bottom', color='#d4af37', fontsize=11, fontweight='bold')
        ax.annotate(f'${target_low:.2f}', (target_low, y_pos - 0.25), 
                    ha='center', va='top', color='#ff4757', fontsize=10)
        ax.annotate(f'${target_mean:.2f}', (target_mean, y_pos - 0.25), 
                    ha='center', va='top', color='#00c896', fontsize=10, fontweight='bold')
        ax.annotate(f'${target_high:.2f}', (target_high, y_pos - 0.25), 
                    ha='center', va='top', color='#6366f1', fontsize=10)
        
        # Upside annotation
        upside = pt.get("upside_pct", 0)
        upside_color = '#00c896' if upside > 0 else '#ff4757'
        ax.annotate(f'Upside: {upside:+.1f}%', (target_mean, y_pos + 0.4), 
                    ha='center', va='bottom', color=upside_color, fontsize=14, fontweight='bold')
        
        # Styling
        ax.set_xlim(min(target_low, current) * 0.9, max(target_high, current) * 1.1)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xlabel('Price ($)', color='#a0a0a8', fontsize=12)
        ax.tick_params(colors='#a0a0a8')
        ax.spines['bottom'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        ax.set_title(f'{ticker} - Analyst Price Targets', 
                     fontsize=16, color='white', fontweight='bold', pad=20)
        
        ax.legend(loc='upper right', facecolor='#1a1a24', edgecolor='#333', 
                  labelcolor='white', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Analyst estimates chart saved to <img {save_path}>"


if __name__ == "__main__":
    # Example usage:
    start_date = "2024-03-01"
    end_date = "2024-04-01"
    save_path = "AAPL_candlestick_chart.png"
    MplFinanceUtils.plot_candlestick_chart("AAPL", start_date, end_date, save_path)
