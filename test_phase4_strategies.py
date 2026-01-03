#!/usr/bin/env python3
"""
Phase 4 Testing - Backtest Strategies (RSI, MACD, Bollinger Bands, MA Ribbon)
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurelius.functional.quantitative import BackTraderUtils

# Test output directory
OUTPUT_DIR = "test_outputs_phase4"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_sma_crossover():
    """Test SMA Crossover strategy (baseline)"""
    print("\n" + "="*60)
    print("TEST: SMA Crossover Strategy")
    print("="*60)
    
    try:
        result = BackTraderUtils.back_test(
            ticker_symbol="AAPL",
            start_date="2023-01-01",
            end_date="2024-12-31",
            strategy="SMA_CrossOver",
            strategy_params='{"fast": 10, "slow": 30}',
            cash=10000.0
        )
        
        if "Final Portfolio Value" in result:
            print(f"✅ PASS | SMA Crossover Strategy")
            # Extract key metrics
            lines = result.split('\n')
            for line in lines[:5]:
                print(f"   {line}")
            return True
        else:
            print(f"❌ FAIL | SMA Crossover Strategy - No results")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | SMA Crossover Strategy")
        print(f"   └─ Error: {e}")
        return False


def test_rsi_strategy():
    """Test RSI Strategy"""
    print("\n" + "="*60)
    print("TEST: RSI Overbought/Oversold Strategy")
    print("="*60)
    
    try:
        result = BackTraderUtils.back_test(
            ticker_symbol="MSFT",
            start_date="2023-01-01",
            end_date="2024-12-31",
            strategy="aurelius.functional.strategies:RSI_Strategy",
            strategy_params='{"period": 14, "oversold": 30, "overbought": 70}',
            cash=10000.0
        )
        
        if "Final Portfolio Value" in result:
            print(f"✅ PASS | RSI Strategy")
            # Extract key metrics
            lines = result.split('\n')
            for line in lines[:5]:
                print(f"   {line}")
            return True
        else:
            print(f"❌ FAIL | RSI Strategy - No results")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | RSI Strategy")
        print(f"   └─ Error: {e}")
        return False


def test_macd_strategy():
    """Test MACD Strategy"""
    print("\n" + "="*60)
    print("TEST: MACD Crossover Strategy")
    print("="*60)
    
    try:
        result = BackTraderUtils.back_test(
            ticker_symbol="GOOGL",
            start_date="2023-01-01",
            end_date="2024-12-31",
            strategy="aurelius.functional.strategies:MACD_Strategy",
            strategy_params='{"fast_period": 12, "slow_period": 26, "signal_period": 9}',
            cash=10000.0
        )
        
        if "Final Portfolio Value" in result:
            print(f"✅ PASS | MACD Strategy")
            # Extract key metrics
            lines = result.split('\n')
            for line in lines[:5]:
                print(f"   {line}")
            return True
        else:
            print(f"❌ FAIL | MACD Strategy - No results")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | MACD Strategy")
        print(f"   └─ Error: {e}")
        return False


def test_bollinger_strategy():
    """Test Bollinger Bands Strategy"""
    print("\n" + "="*60)
    print("TEST: Bollinger Bands Strategy")
    print("="*60)
    
    try:
        result = BackTraderUtils.back_test(
            ticker_symbol="NVDA",
            start_date="2023-01-01",
            end_date="2024-12-31",
            strategy="aurelius.functional.strategies:BollingerBands_Strategy",
            strategy_params='{"period": 20, "devfactor": 2.0}',
            cash=10000.0
        )
        
        if "Final Portfolio Value" in result:
            print(f"✅ PASS | Bollinger Bands Strategy")
            # Extract key metrics
            lines = result.split('\n')
            for line in lines[:5]:
                print(f"   {line}")
            return True
        else:
            print(f"❌ FAIL | Bollinger Bands Strategy - No results")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Bollinger Bands Strategy")
        print(f"   └─ Error: {e}")
        return False


def test_ma_ribbon_strategy():
    """Test Moving Average Ribbon Strategy"""
    print("\n" + "="*60)
    print("TEST: Moving Average Ribbon Strategy")
    print("="*60)
    
    try:
        result = BackTraderUtils.back_test(
            ticker_symbol="TSLA",
            start_date="2023-01-01",
            end_date="2024-12-31",
            strategy="aurelius.functional.strategies:MovingAverageRibbon_Strategy",
            strategy_params='',
            cash=10000.0
        )
        
        if "Final Portfolio Value" in result:
            print(f"✅ PASS | MA Ribbon Strategy")
            # Extract key metrics
            lines = result.split('\n')
            for line in lines[:5]:
                print(f"   {line}")
            return True
        else:
            print(f"❌ FAIL | MA Ribbon Strategy - No results")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | MA Ribbon Strategy")
        print(f"   └─ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🔬 PHASE 4 TESTING: BACKTEST STRATEGIES".center(60))
    print("=" * 60)
    
    results = {
        "SMA Crossover (Baseline)": test_sma_crossover(),
        "RSI Overbought/Oversold": test_rsi_strategy(),
        "MACD Crossover": test_macd_strategy(),
        "Bollinger Bands": test_bollinger_strategy(),
        "MA Ribbon": test_ma_ribbon_strategy(),
    }
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} | {test}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All Phase 4 Strategy tests passed!")
    else:
        print("⚠️  Some tests failed - review output above")

