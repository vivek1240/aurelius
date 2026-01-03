#!/usr/bin/env python3
"""
Phase 4 Testing - Segment Analysis
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurelius.functional import ReportAnalysisUtils

# Test output directory
OUTPUT_DIR = "test_outputs_phase4"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_segment_analysis_msft():
    """Test segment analysis for Microsoft (has clear segments)"""
    print("\n" + "="*60)
    print("TEST: Segment Analysis - Microsoft")
    print("="*60)
    
    try:
        save_path = os.path.join(OUTPUT_DIR, "segment_msft.txt")
        result = ReportAnalysisUtils.analyze_segment_stmt(
            ticker_symbol="MSFT",
            fyear="2023",
            save_path=save_path
        )
        
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                content = f.read()
            
            content_length = len(content)
            print(f"✅ PASS | Segment Analysis (MSFT)")
            print(f"   └─ File: {save_path}")
            print(f"   └─ Content Length: {content_length} chars")
            print(f"   └─ Preview (first 300 chars):")
            print(f"      {content[:300]}...")
            return True
        else:
            print(f"❌ FAIL | Segment Analysis (MSFT) - File not created")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Segment Analysis (MSFT)")
        print(f"   └─ Error: {e}")
        return False


def test_segment_analysis_aapl():
    """Test segment analysis for Apple"""
    print("\n" + "="*60)
    print("TEST: Segment Analysis - Apple")
    print("="*60)
    
    try:
        save_path = os.path.join(OUTPUT_DIR, "segment_aapl.txt")
        result = ReportAnalysisUtils.analyze_segment_stmt(
            ticker_symbol="AAPL",
            fyear="2023",
            save_path=save_path
        )
        
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                content = f.read()
            
            content_length = len(content)
            print(f"✅ PASS | Segment Analysis (AAPL)")
            print(f"   └─ File: {save_path}")
            print(f"   └─ Content Length: {content_length} chars")
            return True
        else:
            print(f"❌ FAIL | Segment Analysis (AAPL) - File not created")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Segment Analysis (AAPL)")
        print(f"   └─ Error: {e}")
        return False


def test_business_highlights():
    """Test business highlights analysis"""
    print("\n" + "="*60)
    print("TEST: Business Highlights")
    print("="*60)
    
    try:
        save_path = os.path.join(OUTPUT_DIR, "business_highlights_nvda.txt")
        result = ReportAnalysisUtils.analyze_business_highlights(
            ticker_symbol="NVDA",
            fyear="2023",
            save_path=save_path
        )
        
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                content = f.read()
            
            content_length = len(content)
            print(f"✅ PASS | Business Highlights (NVDA)")
            print(f"   └─ File: {save_path}")
            print(f"   └─ Content Length: {content_length} chars")
            return True
        else:
            print(f"❌ FAIL | Business Highlights (NVDA) - File not created")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Business Highlights (NVDA)")
        print(f"   └─ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🔬 PHASE 4 TESTING: SEGMENT ANALYSIS".center(60))
    print("=" * 60)
    
    results = {
        "Segment Analysis (MSFT)": test_segment_analysis_msft(),
        "Segment Analysis (AAPL)": test_segment_analysis_aapl(),
        "Business Highlights (NVDA)": test_business_highlights(),
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

