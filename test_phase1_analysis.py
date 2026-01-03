"""
AURELIUS - Phase 1 Testing Script
Test Core Analysis Capabilities

Run with: python test_phase1_analysis.py
"""

import os
import sys
import json
from datetime import datetime

# Add module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test configuration
TEST_TICKER = "AAPL"  # Apple Inc - well-documented, stable data
TEST_YEAR = "2023"
TEST_FILING_DATE = "2023-10-30"  # Apple's FY2023 10-K filing date
TEST_COMPETITORS = ["MSFT", "GOOGL"]
OUTPUT_DIR = "test_outputs/phase1"

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

def test_api_keys():
    """Test that required API keys are configured"""
    print_header("Testing API Key Configuration")
    
    from aurelius.utils import register_keys_from_json
    
    # Try to load API keys
    config_path = os.path.join(os.path.dirname(__file__), "config_api_keys")
    if os.path.exists(config_path):
        register_keys_from_json(config_path)
        print_result("Config file exists", True)
    else:
        print_result("Config file exists", False, "config_api_keys not found")
        return False
    
    # Check individual keys
    keys_to_check = ["FINNHUB_API_KEY", "FMP_API_KEY", "SEC_API_KEY"]
    all_present = True
    for key in keys_to_check:
        present = bool(os.environ.get(key))
        print_result(f"  {key}", present)
        if not present:
            all_present = False
    
    return all_present

def test_yfinance_utils():
    """Test YFinance utilities"""
    print_header("Testing YFinance Utils")
    
    from aurelius.data_source import YFinanceUtils
    
    # Test 1: Get stock info
    try:
        info = YFinanceUtils.get_stock_info(TEST_TICKER)
        has_name = "shortName" in info
        print_result("get_stock_info", has_name, f"Company: {info.get('shortName', 'N/A')}")
    except Exception as e:
        print_result("get_stock_info", False, str(e))
    
    # Test 2: Get stock data
    try:
        data = YFinanceUtils.get_stock_data(TEST_TICKER, "2024-01-01", "2024-01-31")
        has_data = len(data) > 0
        print_result("get_stock_data", has_data, f"Rows: {len(data)}")
    except Exception as e:
        print_result("get_stock_data", False, str(e))
    
    # Test 3: Get income statement
    try:
        income = YFinanceUtils.get_income_stmt(TEST_TICKER)
        has_data = income is not None and len(income) > 0
        print_result("get_income_stmt", has_data, f"Shape: {income.shape if has_data else 'N/A'}")
    except Exception as e:
        print_result("get_income_stmt", False, str(e))
    
    # Test 4: Get balance sheet
    try:
        balance = YFinanceUtils.get_balance_sheet(TEST_TICKER)
        has_data = balance is not None and len(balance) > 0
        print_result("get_balance_sheet", has_data, f"Shape: {balance.shape if has_data else 'N/A'}")
    except Exception as e:
        print_result("get_balance_sheet", False, str(e))
    
    # Test 5: Get cash flow
    try:
        cash_flow = YFinanceUtils.get_cash_flow(TEST_TICKER)
        has_data = cash_flow is not None and len(cash_flow) > 0
        print_result("get_cash_flow", has_data, f"Shape: {cash_flow.shape if has_data else 'N/A'}")
    except Exception as e:
        print_result("get_cash_flow", False, str(e))
    
    # Test 6: Analyst recommendations
    try:
        rating, recs = YFinanceUtils.get_analyst_recommendations(TEST_TICKER)
        has_rating = rating is not None
        print_result("get_analyst_recommendations", has_rating, f"Rating: {rating}")
    except Exception as e:
        print_result("get_analyst_recommendations", False, str(e))

def test_sec_utils():
    """Test SEC utilities"""
    print_header("Testing SEC Utils")
    
    from aurelius.data_source import SECUtils
    
    sections_to_test = [
        (1, "Business Description"),
        ("1A", "Risk Factors"),
        (7, "MD&A"),
    ]
    
    for section_id, section_name in sections_to_test:
        try:
            text = SECUtils.get_10k_section(TEST_TICKER, TEST_YEAR, section_id)
            has_content = text is not None and len(text) > 100
            preview = text[:100].replace('\n', ' ') + "..." if has_content else "No content"
            print_result(f"Section {section_id} ({section_name})", has_content, f"Length: {len(text) if text else 0}")
            if has_content:
                print(f"       └─ Preview: {preview}")
        except Exception as e:
            print_result(f"Section {section_id} ({section_name})", False, str(e)[:80])

def test_fmp_utils():
    """Test FMP utilities"""
    print_header("Testing FMP Utils")
    
    from aurelius.data_source import FMPUtils
    
    # Test 1: SEC report URL
    try:
        result = FMPUtils.get_sec_report(TEST_TICKER, TEST_YEAR)
        has_result = result is not None
        print_result("get_sec_report", has_result, str(result)[:80] if result else "No result")
    except Exception as e:
        print_result("get_sec_report", False, str(e)[:80])
    
    # Test 2: Financial metrics (may require paid tier)
    try:
        metrics = FMPUtils.get_financial_metrics(TEST_TICKER, years=3)
        has_data = metrics is not None and len(metrics) > 0
        print_result("get_financial_metrics", has_data, f"Shape: {metrics.shape if has_data else 'N/A'}")
    except Exception as e:
        error_msg = str(e)
        is_paid_issue = "403" in error_msg or "Legacy" in error_msg or "paid" in error_msg.lower()
        if is_paid_issue:
            print_result("get_financial_metrics", False, "⚠️  Requires FMP paid tier")
        else:
            print_result("get_financial_metrics", False, error_msg[:80])
    
    # Test 3: Target price
    try:
        target = FMPUtils.get_target_price(TEST_TICKER, TEST_FILING_DATE)
        has_target = target is not None
        print_result("get_target_price", has_target, f"Target: ${target}" if target else "No target")
    except Exception as e:
        print_result("get_target_price", False, str(e)[:80])
    
    # Test 4: Historical market cap
    try:
        market_cap = FMPUtils.get_historical_market_cap(TEST_TICKER, TEST_FILING_DATE)
        has_cap = market_cap is not None and market_cap > 0
        cap_str = f"${market_cap/1e9:.2f}B" if has_cap else "N/A"
        print_result("get_historical_market_cap", has_cap, f"Market Cap: {cap_str}")
    except Exception as e:
        print_result("get_historical_market_cap", False, str(e)[:80])

def test_report_analysis_utils():
    """Test Report Analysis utilities"""
    print_header("Testing Report Analysis Utils")
    
    from aurelius.functional.analyzer import ReportAnalysisUtils
    
    # Test 1: Analyze income statement
    try:
        save_path = f"{OUTPUT_DIR}/income_analysis.txt"
        result = ReportAnalysisUtils.analyze_income_stmt(TEST_TICKER, TEST_YEAR, save_path)
        file_exists = os.path.exists(save_path)
        print_result("analyze_income_stmt", file_exists, f"Saved to: {save_path}")
        if file_exists:
            with open(save_path) as f:
                content = f.read()
            print(f"       └─ File size: {len(content)} chars")
    except Exception as e:
        print_result("analyze_income_stmt", False, str(e)[:80])
    
    # Test 2: Analyze balance sheet
    try:
        save_path = f"{OUTPUT_DIR}/balance_analysis.txt"
        result = ReportAnalysisUtils.analyze_balance_sheet(TEST_TICKER, TEST_YEAR, save_path)
        file_exists = os.path.exists(save_path)
        print_result("analyze_balance_sheet", file_exists, f"Saved to: {save_path}")
    except Exception as e:
        print_result("analyze_balance_sheet", False, str(e)[:80])
    
    # Test 3: Analyze cash flow
    try:
        save_path = f"{OUTPUT_DIR}/cashflow_analysis.txt"
        result = ReportAnalysisUtils.analyze_cash_flow(TEST_TICKER, TEST_YEAR, save_path)
        file_exists = os.path.exists(save_path)
        print_result("analyze_cash_flow", file_exists, f"Saved to: {save_path}")
    except Exception as e:
        print_result("analyze_cash_flow", False, str(e)[:80])
    
    # Test 4: Risk assessment
    try:
        save_path = f"{OUTPUT_DIR}/risk_assessment.txt"
        result = ReportAnalysisUtils.get_risk_assessment(TEST_TICKER, TEST_YEAR, save_path)
        file_exists = os.path.exists(save_path)
        print_result("get_risk_assessment", file_exists, f"Saved to: {save_path}")
    except Exception as e:
        print_result("get_risk_assessment", False, str(e)[:80])
    
    # Test 5: Business highlights
    try:
        save_path = f"{OUTPUT_DIR}/business_highlights.txt"
        result = ReportAnalysisUtils.analyze_business_highlights(TEST_TICKER, TEST_YEAR, save_path)
        file_exists = os.path.exists(save_path)
        print_result("analyze_business_highlights", file_exists, f"Saved to: {save_path}")
    except Exception as e:
        print_result("analyze_business_highlights", False, str(e)[:80])
    
    # Test 6: Company description
    try:
        save_path = f"{OUTPUT_DIR}/company_description.txt"
        result = ReportAnalysisUtils.analyze_company_description(TEST_TICKER, TEST_YEAR, save_path)
        file_exists = os.path.exists(save_path)
        print_result("analyze_company_description", file_exists, f"Saved to: {save_path}")
    except Exception as e:
        print_result("analyze_company_description", False, str(e)[:80])
    
    # Test 7: Get key data
    try:
        key_data = ReportAnalysisUtils.get_key_data(TEST_TICKER, TEST_FILING_DATE)
        has_data = key_data is not None and len(key_data) > 0
        print_result("get_key_data", has_data)
        if has_data:
            for k, v in key_data.items():
                print(f"       └─ {k}: {v}")
    except Exception as e:
        print_result("get_key_data", False, str(e)[:80])
    
    # Test 8: Competitors analysis (may fail due to FMP paid tier)
    try:
        save_path = f"{OUTPUT_DIR}/competitors_analysis.txt"
        result = ReportAnalysisUtils.get_competitors_analysis(
            TEST_TICKER, TEST_COMPETITORS, TEST_YEAR, save_path
        )
        file_exists = os.path.exists(save_path)
        print_result("get_competitors_analysis", file_exists, f"Saved to: {save_path}")
    except Exception as e:
        error_msg = str(e)
        is_paid_issue = "403" in error_msg or "Legacy" in error_msg
        if is_paid_issue:
            print_result("get_competitors_analysis", False, "⚠️  Requires FMP paid tier")
        else:
            print_result("get_competitors_analysis", False, error_msg[:80])

def main():
    print("\n" + "🏛️ "*20)
    print("  AURELIUS - Phase 1 Capability Testing")
    print("  Testing Core Analysis Functions")
    print("🏛️ "*20)
    print(f"\nTest Configuration:")
    print(f"  Ticker: {TEST_TICKER}")
    print(f"  Fiscal Year: {TEST_YEAR}")
    print(f"  Filing Date: {TEST_FILING_DATE}")
    print(f"  Competitors: {TEST_COMPETITORS}")
    print(f"  Output Dir: {OUTPUT_DIR}")
    
    # Run tests
    test_api_keys()
    test_yfinance_utils()
    test_sec_utils()
    test_fmp_utils()
    test_report_analysis_utils()
    
    print("\n" + "="*60)
    print("  Phase 1 Testing Complete!")
    print("  Check test_outputs/phase1/ for generated files")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

