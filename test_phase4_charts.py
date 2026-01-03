#!/usr/bin/env python3
"""
Phase 4 Testing - Additional Chart Types (Renko & Point & Figure)
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurelius.functional import MplFinanceUtils

# Test output directory
OUTPUT_DIR = "test_outputs_phase4"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_renko_chart():
    """Test Renko chart generation"""
    print("\n" + "="*60)
    print("TEST: Renko Chart")
    print("="*60)
    
    try:
        save_path = os.path.join(OUTPUT_DIR, "test_renko_AAPL.png")
        result = MplFinanceUtils.plot_stock_price_chart(
            ticker_symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            save_path=save_path,
            type="renko",
            style="charles"  # Good style for renko
        )
        
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"✅ PASS | Renko Chart")
            print(f"   └─ File: {save_path}")
            print(f"   └─ Size: {file_size:,} bytes")
            return True
        else:
            print(f"❌ FAIL | Renko Chart - File not created")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Renko Chart")
        print(f"   └─ Error: {e}")
        return False


def test_pnf_chart():
    """Test Point & Figure chart generation"""
    print("\n" + "="*60)
    print("TEST: Point & Figure Chart")
    print("="*60)
    
    try:
        save_path = os.path.join(OUTPUT_DIR, "test_pnf_AAPL.png")
        result = MplFinanceUtils.plot_stock_price_chart(
            ticker_symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            save_path=save_path,
            type="pnf",
            style="charles"
        )
        
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"✅ PASS | Point & Figure Chart")
            print(f"   └─ File: {save_path}")
            print(f"   └─ Size: {file_size:,} bytes")
            return True
        else:
            print(f"❌ FAIL | Point & Figure Chart - File not created")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Point & Figure Chart")
        print(f"   └─ Error: {e}")
        return False


def test_hollow_filled_chart():
    """Test Hollow and Filled candlestick chart"""
    print("\n" + "="*60)
    print("TEST: Hollow and Filled Chart")
    print("="*60)
    
    try:
        save_path = os.path.join(OUTPUT_DIR, "test_hollow_filled_AAPL.png")
        result = MplFinanceUtils.plot_stock_price_chart(
            ticker_symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            save_path=save_path,
            type="hollow_and_filled",
            style="yahoo"
        )
        
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"✅ PASS | Hollow and Filled Chart")
            print(f"   └─ File: {save_path}")
            print(f"   └─ Size: {file_size:,} bytes")
            return True
        else:
            print(f"❌ FAIL | Hollow and Filled Chart - File not created")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Hollow and Filled Chart")
        print(f"   └─ Error: {e}")
        return False


def test_chart_styles():
    """Test different chart styles"""
    print("\n" + "="*60)
    print("TEST: Chart Styles")
    print("="*60)
    
    styles = ['default', 'charles', 'yahoo', 'nightclouds', 'sas', 'blueskies', 'mike']
    results = {}
    
    for style in styles:
        try:
            save_path = os.path.join(OUTPUT_DIR, f"test_style_{style}.png")
            MplFinanceUtils.plot_stock_price_chart(
                ticker_symbol="MSFT",
                start_date="2024-06-01",
                end_date="2024-12-31",
                save_path=save_path,
                type="candle",
                style=style
            )
            
            if os.path.exists(save_path):
                results[style] = "✅"
            else:
                results[style] = "❌"
        except Exception as e:
            results[style] = f"❌ ({str(e)[:30]})"
    
    print("Style Test Results:")
    for style, status in results.items():
        print(f"   └─ {style}: {status}")
    
    return all(s == "✅" for s in results.values())


if __name__ == "__main__":
    print("\n" + "🔬 PHASE 4 TESTING: ADDITIONAL CHART TYPES".center(60))
    print("=" * 60)
    
    results = {
        "Renko Chart": test_renko_chart(),
        "Point & Figure Chart": test_pnf_chart(),
        "Hollow & Filled Chart": test_hollow_filled_chart(),
        "Chart Styles": test_chart_styles(),
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
        print("🎉 All Phase 4 Chart tests passed!")
    else:
        print("⚠️  Some tests failed - review output above")

