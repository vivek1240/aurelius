"""
AURELIUS - Phase 3 Testing Script
Test PDF Report Generation & RAG

Run with: python test_phase3_reports.py
"""

import os
import sys

# Add module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test configuration
TEST_TICKER = "AAPL"
OUTPUT_DIR = "test_outputs/phase3"

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

def test_report_chart_generation():
    """Test generating charts needed for PDF report"""
    print_header("Testing Report Chart Generation")
    
    from aurelius.functional.charting import ReportChartUtils
    
    # Test 1: Share Performance Chart
    try:
        save_path = f"{OUTPUT_DIR}/{TEST_TICKER}_share_performance.png"
        result = ReportChartUtils.get_share_performance(
            TEST_TICKER,
            "2024-12-31",
            save_path
        )
        file_exists = os.path.exists(save_path)
        file_size = os.path.getsize(save_path) if file_exists else 0
        print_result("Share Performance Chart", file_exists, f"Size: {file_size/1024:.1f}KB")
    except Exception as e:
        print_result("Share Performance Chart", False, str(e)[:80])
    
    # Test 2: PE/EPS Performance Chart
    try:
        save_path = f"{OUTPUT_DIR}/{TEST_TICKER}_pe_eps.png"
        result = ReportChartUtils.get_pe_eps_performance(
            TEST_TICKER,
            "2024-12-31",
            years=4,
            save_path=save_path
        )
        file_exists = os.path.exists(save_path)
        file_size = os.path.getsize(save_path) if file_exists else 0
        print_result("PE/EPS Performance Chart", file_exists, f"Size: {file_size/1024:.1f}KB")
    except Exception as e:
        print_result("PE/EPS Performance Chart", False, str(e)[:80])

def test_pdf_report_generation():
    """Test PDF report generation (requires charts and AI-generated content)"""
    print_header("Testing PDF Report Generation")
    
    from aurelius.functional.reportlab import ReportLabUtils
    
    # Check if we have the required chart files
    share_perf_path = f"{OUTPUT_DIR}/{TEST_TICKER}_share_performance.png"
    pe_eps_path = f"{OUTPUT_DIR}/{TEST_TICKER}_pe_eps.png"
    
    if not os.path.exists(share_perf_path) or not os.path.exists(pe_eps_path):
        print_result("PDF Report Generation", False, "Required chart files not found. Run chart tests first.")
        return
    
    # Sample content (in production, this would be AI-generated)
    sample_business_overview = """
    Apple Inc., founded in 1976, is a multinational technology company that designs, manufactures, 
    and markets smartphones, personal computers, tablets, wearables, and accessories. The company 
    is known for its innovative products including iPhone, Mac, iPad, Apple Watch, and AirPods, 
    along with digital services like the App Store, Apple Music, and Apple TV+.
    """
    
    sample_market_position = """
    Apple maintains a dominant position in the premium smartphone market with approximately 20% 
    global market share. The company serves both consumer and enterprise markets, with strong 
    presence in North America, Europe, and Greater China. Key customers include major retailers, 
    carriers, and direct consumers through Apple Stores.
    """
    
    sample_operating_results = """
    Revenue for FY2024 reached $394.3B, with Services growing to $96.2B (24% of total revenue). 
    iPhone remains the largest segment at $200.6B. Gross margin improved to 46.6%, driven by 
    Services mix. Operating income was $119.4B with 30.3% operating margin.
    """
    
    sample_risk_assessment = """
    Key risks include: 1) Concentration in iPhone (51% of revenue), 2) Supply chain dependence 
    on Asian manufacturing, 3) Regulatory scrutiny on App Store practices, 4) Currency headwinds 
    from strong USD. Downside protections include strong brand, ecosystem lock-in, and $162B cash.
    """
    
    sample_competitors_analysis = """
    Compared to Samsung, Google, and Microsoft: Apple leads in profitability metrics with 30%+ 
    operating margins vs industry 15-20%. Revenue growth trails Samsung in absolute terms but 
    leads in per-unit economics. Services growth outpaces all major competitors.
    """
    
    try:
        pdf_path = f"{OUTPUT_DIR}/{TEST_TICKER}_Equity_Research_Report.pdf"
        
        result = ReportLabUtils.build_annual_report(
            ticker_symbol=TEST_TICKER,
            save_path=OUTPUT_DIR,
            operating_results=sample_operating_results,
            market_position=sample_market_position,
            business_overview=sample_business_overview,
            risk_assessment=sample_risk_assessment,
            competitors_analysis=sample_competitors_analysis,
            share_performance_image_path=share_perf_path,
            pe_eps_performance_image_path=pe_eps_path,
            filing_date="2024-12-31"
        )
        
        # Check if PDF was created
        expected_pdf = f"{OUTPUT_DIR}/{TEST_TICKER}_Equity_Research_report.pdf"
        pdf_exists = os.path.exists(expected_pdf)
        
        if pdf_exists:
            pdf_size = os.path.getsize(expected_pdf)
            print_result("PDF Report Generation", True, f"Size: {pdf_size/1024:.1f}KB")
            print(f"       └─ Report saved to: {expected_pdf}")
        else:
            print_result("PDF Report Generation", False, f"Result: {result[:100]}")
            
    except Exception as e:
        print_result("PDF Report Generation", False, str(e)[:100])

def test_rag_setup():
    """Test RAG (Retrieval Augmented Generation) setup"""
    print_header("Testing RAG Setup")
    
    try:
        from aurelius.functional.rag import get_rag_function
        print_result("RAG Import", True, "get_rag_function available")
        
        # Note: Full RAG testing requires document setup and OpenAI API
        print("       └─ Note: Full RAG testing requires documents & OpenAI API")
        
    except Exception as e:
        print_result("RAG Import", False, str(e)[:80])

def main():
    print("\n" + "📑 "*20)
    print("  AURELIUS - Phase 3 Capability Testing")
    print("  Testing PDF Reports & RAG")
    print("📑 "*20)
    print(f"\nTest Configuration:")
    print(f"  Ticker: {TEST_TICKER}")
    print(f"  Output Dir: {OUTPUT_DIR}")
    
    # Run tests
    test_report_chart_generation()
    test_pdf_report_generation()
    test_rag_setup()
    
    print("\n" + "="*60)
    print("  Phase 3 Testing Complete!")
    print("  Check test_outputs/phase3/ for generated files")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

