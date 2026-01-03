"""
AURELIUS - Phase 2 Testing Script
Test Charting & Backtesting Capabilities

Run with: python test_phase2_charting.py
"""

import os
import sys

# Add module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test configuration
TEST_TICKER = "AAPL"
OUTPUT_DIR = "test_outputs/phase2"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(test_name, success, message=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}")
    if message:
        print(f"       └─ {message}")

def test_mplfinance_charting():
    """Test MplFinance charting utilities"""
    print_header("Testing MplFinance Charting")
    
    from aurelius.functional.charting import MplFinanceUtils
    
    chart_types = [
        ("candle", "Candlestick"),
        ("line", "Line"),
        ("ohlc", "OHLC"),
    ]
    
    for chart_type, chart_name in chart_types:
        try:
            save_path = f"{OUTPUT_DIR}/{TEST_TICKER}_{chart_type}_chart.png"
            result = MplFinanceUtils.plot_stock_price_chart(
                TEST_TICKER,
                "2024-11-01",
                "2024-12-31",
                save_path,
                type=chart_type
            )
            file_exists = os.path.exists(save_path)
            file_size = os.path.getsize(save_path) if file_exists else 0
            print_result(f"{chart_name} Chart", file_exists, f"Size: {file_size/1024:.1f}KB")
        except Exception as e:
            print_result(f"{chart_name} Chart", False, str(e)[:80])
    
    # Test with moving averages
    try:
        save_path = f"{OUTPUT_DIR}/{TEST_TICKER}_line_ma_chart.png"
        result = MplFinanceUtils.plot_stock_price_chart(
            TEST_TICKER,
            "2024-06-01",
            "2024-12-31",
            save_path,
            type="line",
            mav=(20, 50)
        )
        file_exists = os.path.exists(save_path)
        print_result("Line Chart with MA(20,50)", file_exists)
    except Exception as e:
        print_result("Line Chart with MA(20,50)", False, str(e)[:80])

def test_report_chart_utils():
    """Test Report Chart utilities"""
    print_header("Testing Report Chart Utils")
    
    from aurelius.functional.charting import ReportChartUtils
    
    # Test 1: Share performance vs S&P 500
    try:
        save_path = f"{OUTPUT_DIR}/{TEST_TICKER}_share_performance.png"
        result = ReportChartUtils.get_share_performance(
            TEST_TICKER,
            "2024-12-31",
            save_path
        )
        file_exists = os.path.exists(save_path)
        file_size = os.path.getsize(save_path) if file_exists else 0
        print_result("Share Performance vs S&P 500", file_exists, f"Size: {file_size/1024:.1f}KB")
    except Exception as e:
        print_result("Share Performance vs S&P 500", False, str(e)[:80])
    
    # Test 2: PE/EPS Performance
    try:
        save_path = f"{OUTPUT_DIR}/{TEST_TICKER}_pe_eps_performance.png"
        result = ReportChartUtils.get_pe_eps_performance(
            TEST_TICKER,
            "2024-12-31",
            years=4,
            save_path=save_path
        )
        file_exists = os.path.exists(save_path)
        file_size = os.path.getsize(save_path) if file_exists else 0
        print_result("PE & EPS Performance", file_exists, f"Size: {file_size/1024:.1f}KB")
    except Exception as e:
        print_result("PE & EPS Performance", False, str(e)[:80])

def test_backtrader_utils():
    """Test BackTrader utilities"""
    print_header("Testing BackTrader Backtesting")
    
    from aurelius.functional.quantitative import BackTraderUtils
    
    # Test 1: SMA Crossover strategy
    try:
        save_path = f"{OUTPUT_DIR}/{TEST_TICKER}_backtest.png"
        result = BackTraderUtils.back_test(
            TEST_TICKER,
            "2023-01-01",
            "2024-12-31",
            strategy="SMA_CrossOver",
            strategy_params='{"fast": 10, "slow": 30}',
            cash=10000.0,
            save_fig=save_path
        )
        has_result = "Portfolio Value" in result
        print_result("SMA Crossover Backtest", has_result)
        if has_result:
            # Extract key metrics from result
            lines = result.split('\n')
            for line in lines:
                if "Final Portfolio Value" in line or "Sharpe Ratio" in line:
                    print(f"       └─ {line.strip()}")
    except Exception as e:
        print_result("SMA Crossover Backtest", False, str(e)[:80])

def main():
    print("\n" + "📊 "*20)
    print("  AURELIUS - Phase 2 Capability Testing")
    print("  Testing Charting & Backtesting")
    print("📊 "*20)
    print(f"\nTest Configuration:")
    print(f"  Ticker: {TEST_TICKER}")
    print(f"  Output Dir: {OUTPUT_DIR}")
    
    # Run tests
    test_mplfinance_charting()
    test_report_chart_utils()
    test_backtrader_utils()
    
    print("\n" + "="*60)
    print("  Phase 2 Testing Complete!")
    print("  Check test_outputs/phase2/ for generated charts")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

