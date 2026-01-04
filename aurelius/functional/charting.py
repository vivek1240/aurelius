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


class OwnershipCharts:
    """Charts for ownership analysis visualization"""
    
    @staticmethod
    def ownership_pie_chart(
        ticker: str,
        save_path: str = None
    ) -> str:
        """
        Create a pie chart showing ownership breakdown
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .ownership import OwnershipIntel
        
        # Get ownership data
        breakdown = OwnershipIntel.get_ownership_breakdown(ticker)
        
        if 'error' in breakdown:
            return f"Error getting ownership data: {breakdown['error']}"
        
        # Setup data
        labels = ['Institutions', 'Insiders', 'Public/Other']
        sizes = [
            breakdown.get('institutions_percent', 0),
            breakdown.get('insiders_percent', 0),
            breakdown.get('public_percent', 0)
        ]
        colors = ['#d4af37', '#00c896', '#6366f1']
        explode = (0.02, 0.02, 0.02)
        
        # Setup plot
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('#0d0d12')
        ax.set_facecolor('#0d0d12')
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%',
            explode=explode,
            startangle=90,
            pctdistance=0.75,
            textprops={'color': 'white', 'fontsize': 12}
        )
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
            autotext.set_fontweight('bold')
        
        # Add center circle for donut effect
        centre_circle = plt.Circle((0, 0), 0.50, fc='#0d0d12')
        ax.add_artist(centre_circle)
        
        # Add institution count in center
        inst_count = breakdown.get('institutions_count', 0)
        ax.text(0, 0, f'{inst_count:,}\nInstitutions', 
                ha='center', va='center', color='white', fontsize=14, fontweight='bold')
        
        ax.set_title(f'{ticker} Ownership Breakdown', 
                     fontsize=16, color='white', fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Ownership pie chart saved to <img {save_path}>"
    
    @staticmethod
    def top_holders_chart(
        ticker: str,
        holder_type: str = 'institutional',
        top_n: int = 10,
        save_path: str = None
    ) -> str:
        """
        Create a horizontal bar chart of top holders
        
        Args:
            ticker: Stock ticker symbol
            holder_type: 'institutional' or 'mutual_fund'
            top_n: Number of top holders to show
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .ownership import OwnershipIntel
        
        # Get holder data
        if holder_type == 'institutional':
            holders_df = OwnershipIntel.get_institutional_holders(ticker, top_n)
            title_prefix = "Top Institutional"
        else:
            holders_df = OwnershipIntel.get_mutual_fund_holders(ticker, top_n)
            title_prefix = "Top Mutual Fund"
        
        if holders_df.empty or 'error' in holders_df.columns:
            return f"No {holder_type} holder data available"
        
        # Prepare data - limit to top_n
        df = holders_df.head(top_n).copy()
        
        if 'Holder' not in df.columns or 'Value (B)' not in df.columns:
            # Try to use raw Value column
            if 'Value' in df.columns:
                df['Value (B)'] = df['Value'] / 1e9
            else:
                return "Incomplete holder data"
        
        # Reverse for horizontal bar chart (top at top)
        df = df.iloc[::-1]
        
        # Setup plot
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('#0d0d12')
        ax.set_facecolor('#0d0d12')
        
        # Create horizontal bar chart
        y_pos = np.arange(len(df))
        colors = plt.cm.YlOrBr(np.linspace(0.3, 0.9, len(df)))
        
        bars = ax.barh(y_pos, df['Value (B)'], color=colors, alpha=0.9)
        
        # Add value labels
        for bar, val in zip(bars, df['Value (B)']):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f'${val:.1f}B', ha='left', va='center', 
                    color='white', fontsize=10)
        
        # Truncate long holder names
        holder_names = [h[:35] + '...' if len(str(h)) > 35 else str(h) 
                       for h in df['Holder']]
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(holder_names)
        ax.set_xlabel('Holdings Value ($B)', color='#a0a0a8', fontsize=12)
        
        ax.tick_params(colors='#a0a0a8')
        ax.spines['bottom'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#333')
        ax.grid(True, alpha=0.1, color='white', axis='x')
        
        ax.set_title(f'{ticker} - {title_prefix} Holders', 
                     fontsize=16, color='white', fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Top holders chart saved to <img {save_path}>"
    
    @staticmethod
    def insider_activity_chart(
        ticker: str,
        save_path: str = None
    ) -> str:
        """
        Create a chart showing insider buying vs selling activity
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .ownership import OwnershipIntel
        
        # Get insider data
        summary = OwnershipIntel.get_insider_summary(ticker)
        
        if 'error' in summary:
            return f"Error getting insider data: {summary['error']}"
        
        # Setup data
        categories = ['Purchases', 'Sales']
        shares = [
            summary.get('purchases_shares', 0) / 1e6,  # Convert to millions
            summary.get('sales_shares', 0) / 1e6
        ]
        counts = [
            summary.get('purchases_count', 0),
            summary.get('sales_count', 0)
        ]
        colors = ['#00c896', '#ff4757']
        
        # Setup plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0d0d12')
        
        # Left chart: Shares traded
        ax1.set_facecolor('#0d0d12')
        bars1 = ax1.bar(categories, shares, color=colors, alpha=0.9)
        
        for bar, val in zip(bars1, shares):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                     f'{val:.2f}M', ha='center', va='bottom', 
                     color='white', fontsize=12, fontweight='bold')
        
        ax1.set_ylabel('Shares (Millions)', color='#a0a0a8', fontsize=12)
        ax1.set_title('Shares Traded', fontsize=14, color='white', fontweight='bold')
        ax1.tick_params(colors='#a0a0a8')
        ax1.spines['bottom'].set_color('#333')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#333')
        ax1.grid(True, alpha=0.1, color='white', axis='y')
        
        # Right chart: Transaction count
        ax2.set_facecolor('#0d0d12')
        bars2 = ax2.bar(categories, counts, color=colors, alpha=0.9)
        
        for bar, val in zip(bars2, counts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                     f'{int(val)}', ha='center', va='bottom', 
                     color='white', fontsize=12, fontweight='bold')
        
        ax2.set_ylabel('Number of Transactions', color='#a0a0a8', fontsize=12)
        ax2.set_title('Transaction Count', fontsize=14, color='white', fontweight='bold')
        ax2.tick_params(colors='#a0a0a8')
        ax2.spines['bottom'].set_color('#333')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#333')
        ax2.grid(True, alpha=0.1, color='white', axis='y')
        
        # Add sentiment indicator
        sentiment = summary.get('sentiment', 'Neutral')
        sentiment_color = '#00c896' if 'Bullish' in sentiment else ('#ff4757' if 'Bearish' in sentiment else '#a0a0a8')
        
        # Main title (without sentiment to avoid duplication)
        fig.suptitle(f'{ticker} - Insider Activity (Last 6 Months)', 
                     fontsize=16, color='white', fontweight='bold', y=1.02)
        # Sentiment subtitle with color coding
        fig.text(0.5, 0.95, f'Sentiment: {sentiment}', ha='center', 
                 fontsize=12, color=sentiment_color, fontweight='bold')
        
        plt.tight_layout(rect=[0, 0, 1, 0.93])
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Insider activity chart saved to <img {save_path}>"
    
    @staticmethod
    def ownership_comparison_chart(
        tickers: list,
        save_path: str = None
    ) -> str:
        """
        Compare ownership structure across multiple stocks
        
        Args:
            tickers: List of stock ticker symbols
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .ownership import OwnershipIntel
        
        # Get comparison data
        comparison_df = OwnershipIntel.get_ownership_comparison(tickers)
        
        if comparison_df.empty:
            return "No ownership comparison data available"
        
        # Setup plot
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('#0d0d12')
        ax.set_facecolor('#0d0d12')
        
        x = np.arange(len(tickers))
        width = 0.25
        
        # Get values (handle N/A and Error values)
        def safe_float(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0
        
        insider_vals = [safe_float(comparison_df[comparison_df['Ticker'] == t]['Insider %'].values[0]) 
                       for t in tickers]
        inst_vals = [safe_float(comparison_df[comparison_df['Ticker'] == t]['Institution %'].values[0]) 
                    for t in tickers]
        public_vals = [safe_float(comparison_df[comparison_df['Ticker'] == t]['Public %'].values[0]) 
                      for t in tickers]
        
        # Create grouped bar chart
        bars1 = ax.bar(x - width, insider_vals, width, label='Insiders', color='#00c896', alpha=0.9)
        bars2 = ax.bar(x, inst_vals, width, label='Institutions', color='#d4af37', alpha=0.9)
        bars3 = ax.bar(x + width, public_vals, width, label='Public', color='#6366f1', alpha=0.9)
        
        ax.set_ylabel('Ownership (%)', color='#a0a0a8', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(tickers)
        
        ax.tick_params(colors='#a0a0a8')
        ax.spines['bottom'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#333')
        ax.grid(True, alpha=0.1, color='white', axis='y')
        
        ax.legend(loc='upper right', facecolor='#1a1a24', edgecolor='#333', 
                  labelcolor='white', fontsize=10)
        
        ax.set_title('Ownership Structure Comparison', 
                     fontsize=16, color='white', fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Ownership comparison chart saved to <img {save_path}>"


class DCFCharts:
    """Charts for DCF valuation visualization"""
    
    @staticmethod
    def projection_chart(
        ticker: str,
        save_path: str = None
    ) -> str:
        """
        Create revenue and FCF projection chart
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .dcf import DCFModel
        
        # Get historical and projected data
        historical = DCFModel.get_historical_financials(ticker, 3)
        projections = DCFModel.project_financials(ticker, 5)
        
        if "error" in historical or "error" in projections:
            return "Error getting data for projection chart"
        
        # Setup plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        fig.patch.set_facecolor('#0d0d12')
        
        # Prepare data
        hist_years = historical["years"][::-1]  # Reverse to chronological
        hist_revenue = [r/1e9 for r in historical["revenue"][::-1]]  # In billions
        hist_fcf = [f/1e9 for f in historical["free_cash_flow"][::-1]]
        
        proj_years = projections["years"]
        proj_revenue = [r/1e9 for r in projections["revenue"]]
        proj_fcf = [f/1e9 for f in projections["free_cash_flow"]]
        
        all_years = hist_years + proj_years
        all_revenue = hist_revenue + proj_revenue
        all_fcf = hist_fcf + proj_fcf
        
        x = np.arange(len(all_years))
        hist_len = len(hist_years)
        
        # Left chart: Revenue
        ax1.set_facecolor('#0d0d12')
        colors1 = ['#d4af37'] * hist_len + ['#d4af37'] * len(proj_years)
        alphas1 = [0.9] * hist_len + [0.5] * len(proj_years)
        
        bars1 = ax1.bar(x[:hist_len], all_revenue[:hist_len], color='#d4af37', alpha=0.9, label='Historical')
        bars2 = ax1.bar(x[hist_len:], all_revenue[hist_len:], color='#d4af37', alpha=0.5, label='Projected', hatch='//')
        
        # Add growth rate labels
        for i in range(1, len(all_revenue)):
            if all_revenue[i-1] > 0:
                growth = ((all_revenue[i] - all_revenue[i-1]) / all_revenue[i-1]) * 100
                ax1.annotate(f'{growth:+.0f}%', (x[i], all_revenue[i] + 2), 
                            ha='center', va='bottom', color='#00c896', fontsize=8)
        
        ax1.set_ylabel('Revenue ($B)', color='#a0a0a8', fontsize=12)
        ax1.set_title(f'{ticker} Revenue Projections', fontsize=14, color='white', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(all_years, rotation=45, ha='right')
        ax1.tick_params(colors='#a0a0a8')
        ax1.axvline(x=hist_len - 0.5, color='white', linestyle='--', alpha=0.3)
        ax1.spines['bottom'].set_color('#333')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#333')
        ax1.grid(True, alpha=0.1, color='white', axis='y')
        ax1.legend(loc='upper left', facecolor='#1a1a24', edgecolor='#333', labelcolor='white')
        
        # Right chart: Free Cash Flow
        ax2.set_facecolor('#0d0d12')
        bars3 = ax2.bar(x[:hist_len], all_fcf[:hist_len], color='#00c896', alpha=0.9, label='Historical')
        bars4 = ax2.bar(x[hist_len:], all_fcf[hist_len:], color='#00c896', alpha=0.5, label='Projected', hatch='//')
        
        ax2.set_ylabel('Free Cash Flow ($B)', color='#a0a0a8', fontsize=12)
        ax2.set_title(f'{ticker} FCF Projections', fontsize=14, color='white', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(all_years, rotation=45, ha='right')
        ax2.tick_params(colors='#a0a0a8')
        ax2.axvline(x=hist_len - 0.5, color='white', linestyle='--', alpha=0.3)
        ax2.spines['bottom'].set_color('#333')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#333')
        ax2.grid(True, alpha=0.1, color='white', axis='y')
        ax2.legend(loc='upper left', facecolor='#1a1a24', edgecolor='#333', labelcolor='white')
        
        plt.suptitle(f'{ticker} - DCF Projection Chart', fontsize=16, color='white', fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"DCF projection chart saved to <img {save_path}>"
    
    @staticmethod
    def sensitivity_heatmap(
        ticker: str,
        save_path: str = None
    ) -> str:
        """
        Create sensitivity analysis heatmap
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .dcf import DCFModel
        
        # Get sensitivity data
        sensitivity = DCFModel.sensitivity_analysis(ticker)
        
        if "error" in sensitivity:
            return f"Error creating sensitivity heatmap: {sensitivity['error']}"
        
        matrix = np.array(sensitivity["matrix"])
        current_price = sensitivity["current_price"]
        wacc_labels = sensitivity["wacc_values"]
        growth_labels = sensitivity["growth_values"]
        
        # Setup plot
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('#0d0d12')
        ax.set_facecolor('#0d0d12')
        
        # Create heatmap
        # Color scale: green for values > current_price, red for values < current_price
        norm_matrix = (matrix - current_price) / current_price
        
        # Custom colormap
        from matplotlib.colors import LinearSegmentedColormap
        colors_list = ['#ff4757', '#2d2d3a', '#00c896']
        cmap = LinearSegmentedColormap.from_list('dcf', colors_list)
        
        im = ax.imshow(norm_matrix, cmap=cmap, aspect='auto', vmin=-0.5, vmax=0.5)
        
        # Add value annotations
        for i in range(len(wacc_labels)):
            for j in range(len(growth_labels)):
                val = matrix[i][j]
                text_color = 'white' if abs(val - current_price) / current_price > 0.2 else '#a0a0a8'
                ax.text(j, i, f'${val:.0f}', ha='center', va='center', 
                       color=text_color, fontsize=10, fontweight='bold')
        
        # Labels
        ax.set_xticks(np.arange(len(growth_labels)))
        ax.set_yticks(np.arange(len(wacc_labels)))
        ax.set_xticklabels(growth_labels, color='#a0a0a8')
        ax.set_yticklabels(wacc_labels, color='#a0a0a8')
        ax.set_xlabel('Terminal Growth Rate', color='#a0a0a8', fontsize=12)
        ax.set_ylabel('WACC', color='#a0a0a8', fontsize=12)
        
        ax.set_title(f'{ticker} DCF Sensitivity Analysis\nCurrent Price: ${current_price:.2f}', 
                     fontsize=14, color='white', fontweight='bold', pad=20)
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('vs Current Price', color='#a0a0a8')
        cbar.ax.yaxis.set_tick_params(color='#a0a0a8')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#a0a0a8')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Sensitivity heatmap saved to <img {save_path}>"
    
    @staticmethod
    def valuation_waterfall(
        ticker: str,
        save_path: str = None
    ) -> str:
        """
        Create valuation waterfall chart
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save the chart
        
        Returns:
            Path to saved chart
        """
        from .dcf import DCFModel
        
        # Get DCF data
        dcf = DCFModel.calculate_dcf(ticker)
        
        if "error" in dcf:
            return f"Error creating waterfall chart: {dcf['error']}"
        
        v = dcf["valuation"]
        
        # Waterfall data
        labels = ['PV of FCFs', 'PV of Terminal\nValue', 'Enterprise\nValue', 'Less: Net Debt', 'Equity Value']
        values = [v['pv_of_fcfs'], v['pv_of_terminal_value'], 0, -v['net_debt'], 0]
        cumulative = [v['pv_of_fcfs'], v['pv_of_fcfs'] + v['pv_of_terminal_value'], 
                     v['enterprise_value'], v['enterprise_value'] - v['net_debt'], v['equity_value']]
        
        # Setup plot
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('#0d0d12')
        ax.set_facecolor('#0d0d12')
        
        colors = ['#d4af37', '#d4af37', '#6366f1', '#ff4757' if v['net_debt'] > 0 else '#00c896', '#00c896']
        
        # Create waterfall
        x = np.arange(len(labels))
        bar_width = 0.6
        
        # Starting positions for bars
        bottoms = [0, v['pv_of_fcfs'], 0, v['enterprise_value'], 0]
        heights = [v['pv_of_fcfs'], v['pv_of_terminal_value'], v['enterprise_value'], 
                   abs(v['net_debt']), v['equity_value']]
        
        bars = ax.bar(x, heights, bar_width, bottom=bottoms, color=colors, alpha=0.9)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, heights)):
            height = bar.get_height()
            bottom = bar.get_y()
            ax.text(bar.get_x() + bar.get_width()/2, bottom + height/2, 
                   f'${val:.1f}B', ha='center', va='center', 
                   color='white', fontsize=11, fontweight='bold')
        
        # Connect lines
        for i in range(len(x) - 1):
            if i != 2:  # Skip the EV bar connection
                ax.plot([x[i] + bar_width/2, x[i+1] - bar_width/2], 
                       [cumulative[i], cumulative[i]], color='white', linestyle='--', alpha=0.3)
        
        ax.set_xticks(x)
        ax.set_xticklabels(labels, color='#a0a0a8', fontsize=10)
        ax.set_ylabel('Value ($B)', color='#a0a0a8', fontsize=12)
        ax.tick_params(colors='#a0a0a8')
        ax.spines['bottom'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#333')
        ax.grid(True, alpha=0.1, color='white', axis='y')
        
        # Add intrinsic value annotation
        ax.annotate(f'Intrinsic Value: ${v["intrinsic_value_per_share"]:.2f}/share\n'
                   f'Current: ${v["current_price"]:.2f} ({v["upside_percent"]:+.1f}%)',
                   xy=(4, v['equity_value']), xytext=(3.5, v['equity_value'] * 0.7),
                   fontsize=12, color='white', fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='#1a1a24', edgecolor='#333'),
                   arrowprops=dict(arrowstyle='->', color='white', alpha=0.5))
        
        ax.set_title(f'{ticker} - DCF Valuation Waterfall', 
                     fontsize=16, color='white', fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='#0d0d12', edgecolor='none', 
                        bbox_inches='tight', dpi=150)
        plt.close()
        
        return f"Valuation waterfall chart saved to <img {save_path}>"


if __name__ == "__main__":
    # Example usage:
    start_date = "2024-03-01"
    end_date = "2024-04-01"
    save_path = "AAPL_candlestick_chart.png"
    MplFinanceUtils.plot_candlestick_chart("AAPL", start_date, end_date, save_path)
