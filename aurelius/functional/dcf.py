"""
DCF (Discounted Cash Flow) Valuation Model for Ikshvaku

Provides comprehensive DCF analysis including:
- Revenue and earnings projections
- WACC calculation (Cost of Equity + Cost of Debt)
- Free Cash Flow projections
- Terminal Value calculation
- Intrinsic value per share
- Sensitivity analysis
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf


class DCFModel:
    """Discounted Cash Flow Valuation Model"""
    
    # Market assumptions (can be overridden)
    RISK_FREE_RATE = 0.045  # 10Y Treasury ~4.5%
    MARKET_RISK_PREMIUM = 0.055  # Historical equity risk premium ~5.5%
    DEFAULT_TERMINAL_GROWTH = 0.025  # 2.5% long-term GDP growth
    DEFAULT_TAX_RATE = 0.21  # US corporate tax rate
    
    @staticmethod
    def get_historical_financials(ticker: str, years: int = 5) -> Dict[str, Any]:
        """
        Get historical financial data for DCF analysis.
        
        Args:
            ticker: Stock ticker symbol
            years: Number of years of history
            
        Returns:
            Dictionary with historical financials
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get financial statements
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            info = stock.info
            
            if income_stmt is None or income_stmt.empty:
                return {"error": f"No financial data for {ticker}"}
            
            # Extract key metrics
            historical = {
                "ticker": ticker,
                "company_name": info.get("shortName", ticker),
                "currency": info.get("currency", "USD"),
                "years": [],
                "revenue": [],
                "operating_income": [],
                "net_income": [],
                "operating_cash_flow": [],
                "capex": [],
                "free_cash_flow": [],
                "gross_margin": [],
                "operating_margin": [],
                "net_margin": []
            }
            
            # Get available years (columns are dates)
            available_years = min(years, len(income_stmt.columns))
            
            for i in range(available_years):
                col = income_stmt.columns[i]
                year = col.year if hasattr(col, 'year') else str(col)[:4]
                
                # Revenue
                revenue = income_stmt.loc['Total Revenue', col] if 'Total Revenue' in income_stmt.index else 0
                
                # Operating Income
                op_income = income_stmt.loc['Operating Income', col] if 'Operating Income' in income_stmt.index else 0
                
                # Net Income
                net_income = income_stmt.loc['Net Income', col] if 'Net Income' in income_stmt.index else 0
                
                # Cash Flow items
                if cash_flow is not None and not cash_flow.empty and col in cash_flow.columns:
                    ocf = cash_flow.loc['Operating Cash Flow', col] if 'Operating Cash Flow' in cash_flow.index else 0
                    capex = abs(cash_flow.loc['Capital Expenditure', col]) if 'Capital Expenditure' in cash_flow.index else 0
                else:
                    ocf = 0
                    capex = 0
                
                fcf = ocf - capex if ocf and capex else 0
                
                historical["years"].append(year)
                historical["revenue"].append(float(revenue) if revenue else 0)
                historical["operating_income"].append(float(op_income) if op_income else 0)
                historical["net_income"].append(float(net_income) if net_income else 0)
                historical["operating_cash_flow"].append(float(ocf) if ocf else 0)
                historical["capex"].append(float(capex) if capex else 0)
                historical["free_cash_flow"].append(float(fcf) if fcf else 0)
                
                # Calculate margins
                if revenue and revenue > 0:
                    gross_profit = income_stmt.loc['Gross Profit', col] if 'Gross Profit' in income_stmt.index else 0
                    historical["gross_margin"].append(round((float(gross_profit) / float(revenue)) * 100, 2) if gross_profit else 0)
                    historical["operating_margin"].append(round((float(op_income) / float(revenue)) * 100, 2) if op_income else 0)
                    historical["net_margin"].append(round((float(net_income) / float(revenue)) * 100, 2) if net_income else 0)
                else:
                    historical["gross_margin"].append(0)
                    historical["operating_margin"].append(0)
                    historical["net_margin"].append(0)
            
            # Get current stock info
            historical["current_price"] = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            historical["shares_outstanding"] = info.get("sharesOutstanding", 0)
            historical["market_cap"] = info.get("marketCap", 0)
            historical["beta"] = info.get("beta", 1.0)
            historical["total_debt"] = info.get("totalDebt", 0)
            historical["total_cash"] = info.get("totalCash", 0)
            historical["enterprise_value"] = info.get("enterpriseValue", 0)
            
            # Calculate historical growth rates
            if len(historical["revenue"]) >= 2:
                revenues = [r for r in historical["revenue"] if r > 0]
                if len(revenues) >= 2:
                    # CAGR calculation
                    historical["revenue_cagr"] = round(
                        ((revenues[0] / revenues[-1]) ** (1 / (len(revenues) - 1)) - 1) * 100, 2
                    )
                else:
                    historical["revenue_cagr"] = 0
            else:
                historical["revenue_cagr"] = 0
            
            return historical
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def calculate_wacc(
        ticker: str,
        risk_free_rate: float = None,
        market_risk_premium: float = None,
        tax_rate: float = None
    ) -> Dict[str, Any]:
        """
        Calculate Weighted Average Cost of Capital (WACC).
        
        WACC = (E/V × Re) + (D/V × Rd × (1-T))
        
        Where:
        - E = Market value of equity
        - D = Market value of debt
        - V = E + D
        - Re = Cost of equity (CAPM)
        - Rd = Cost of debt
        - T = Tax rate
        
        Args:
            ticker: Stock ticker symbol
            risk_free_rate: Risk-free rate (default: 4.5%)
            market_risk_premium: Market risk premium (default: 5.5%)
            tax_rate: Corporate tax rate (default: 21%)
            
        Returns:
            Dictionary with WACC components
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            
            # Use defaults if not provided
            rf = risk_free_rate or DCFModel.RISK_FREE_RATE
            mrp = market_risk_premium or DCFModel.MARKET_RISK_PREMIUM
            tax = tax_rate or DCFModel.DEFAULT_TAX_RATE
            
            # Get beta
            beta = info.get("beta", 1.0) or 1.0
            
            # Cost of Equity using CAPM: Re = Rf + β(Rm - Rf)
            cost_of_equity = rf + (beta * mrp)
            
            # Get debt and equity values
            market_cap = info.get("marketCap", 0) or 0
            total_debt = info.get("totalDebt", 0) or 0
            
            # Cost of Debt
            # Try to calculate from interest expense / total debt
            interest_expense = 0
            if income_stmt is not None and not income_stmt.empty:
                if 'Interest Expense' in income_stmt.index:
                    interest_expense = abs(float(income_stmt.loc['Interest Expense'].iloc[0] or 0))
            
            if total_debt > 0 and interest_expense > 0:
                cost_of_debt = interest_expense / total_debt
            else:
                # Default assumption for cost of debt
                cost_of_debt = rf + 0.02  # Risk-free + 2% credit spread
            
            # Calculate weights
            total_value = market_cap + total_debt
            if total_value > 0:
                equity_weight = market_cap / total_value
                debt_weight = total_debt / total_value
            else:
                equity_weight = 1.0
                debt_weight = 0.0
            
            # WACC = (E/V × Re) + (D/V × Rd × (1-T))
            wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax))
            
            return {
                "ticker": ticker,
                "wacc": round(wacc * 100, 2),  # As percentage
                "wacc_decimal": round(wacc, 4),
                "cost_of_equity": round(cost_of_equity * 100, 2),
                "cost_of_debt": round(cost_of_debt * 100, 2),
                "cost_of_debt_after_tax": round(cost_of_debt * (1 - tax) * 100, 2),
                "beta": round(beta, 2),
                "risk_free_rate": round(rf * 100, 2),
                "market_risk_premium": round(mrp * 100, 2),
                "tax_rate": round(tax * 100, 2),
                "equity_weight": round(equity_weight * 100, 2),
                "debt_weight": round(debt_weight * 100, 2),
                "market_cap": market_cap,
                "total_debt": total_debt
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def project_financials(
        ticker: str,
        years: int = 5,
        revenue_growth_rates: List[float] = None,
        operating_margin_targets: List[float] = None
    ) -> Dict[str, Any]:
        """
        Project future financials for DCF.
        
        Args:
            ticker: Stock ticker symbol
            years: Number of years to project
            revenue_growth_rates: List of growth rates for each year (e.g., [0.25, 0.20, 0.15, 0.10, 0.08])
            operating_margin_targets: List of operating margins for each year
            
        Returns:
            Dictionary with projected financials
        """
        try:
            # Get historical data
            historical = DCFModel.get_historical_financials(ticker, 3)
            
            if "error" in historical:
                return historical
            
            # Get most recent figures
            if not historical["revenue"]:
                return {"error": "No revenue data available"}
            
            last_revenue = historical["revenue"][0]
            last_op_margin = historical["operating_margin"][0] / 100 if historical["operating_margin"] else 0.15
            last_fcf = historical["free_cash_flow"][0] if historical["free_cash_flow"] else 0
            
            # Default growth rates if not provided (declining growth assumption)
            if revenue_growth_rates is None:
                base_growth = historical.get("revenue_cagr", 10) / 100
                revenue_growth_rates = [
                    min(base_growth, 0.30),
                    min(base_growth * 0.85, 0.25),
                    min(base_growth * 0.70, 0.20),
                    min(base_growth * 0.55, 0.15),
                    min(base_growth * 0.40, 0.10)
                ][:years]
            
            # Default operating margin targets (slight compression for high-margin companies)
            if operating_margin_targets is None:
                if last_op_margin > 0.30:
                    operating_margin_targets = [last_op_margin - (i * 0.01) for i in range(years)]
                else:
                    operating_margin_targets = [last_op_margin + (i * 0.005) for i in range(years)]
            
            # Project financials
            projections = {
                "ticker": ticker,
                "base_year": historical["years"][0] if historical["years"] else "Current",
                "base_revenue": last_revenue,
                "projection_years": years,
                "years": [],
                "revenue": [],
                "revenue_growth": [],
                "operating_income": [],
                "operating_margin": [],
                "free_cash_flow": [],
                "fcf_margin": []
            }
            
            current_revenue = last_revenue
            
            # Estimate FCF as % of operating income (historical ratio)
            if historical["operating_income"][0] and historical["free_cash_flow"][0]:
                fcf_to_oi_ratio = historical["free_cash_flow"][0] / historical["operating_income"][0]
            else:
                fcf_to_oi_ratio = 0.80  # Default 80% conversion
            
            for i in range(years):
                growth = revenue_growth_rates[i] if i < len(revenue_growth_rates) else revenue_growth_rates[-1]
                op_margin = operating_margin_targets[i] if i < len(operating_margin_targets) else operating_margin_targets[-1]
                
                projected_revenue = current_revenue * (1 + growth)
                projected_op_income = projected_revenue * op_margin
                projected_fcf = projected_op_income * fcf_to_oi_ratio
                
                year_label = f"Year {i + 1}"
                
                projections["years"].append(year_label)
                projections["revenue"].append(round(projected_revenue, 0))
                projections["revenue_growth"].append(round(growth * 100, 1))
                projections["operating_income"].append(round(projected_op_income, 0))
                projections["operating_margin"].append(round(op_margin * 100, 1))
                projections["free_cash_flow"].append(round(projected_fcf, 0))
                projections["fcf_margin"].append(round((projected_fcf / projected_revenue) * 100, 1))
                
                current_revenue = projected_revenue
            
            return projections
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def calculate_dcf(
        ticker: str,
        projection_years: int = 5,
        revenue_growth_rates: List[float] = None,
        operating_margin_targets: List[float] = None,
        terminal_growth_rate: float = None,
        wacc_override: float = None
    ) -> Dict[str, Any]:
        """
        Calculate full DCF valuation.
        
        Args:
            ticker: Stock ticker symbol
            projection_years: Number of years to project
            revenue_growth_rates: Custom growth rates
            operating_margin_targets: Custom margin targets
            terminal_growth_rate: Long-term growth rate (default 2.5%)
            wacc_override: Override calculated WACC
            
        Returns:
            Complete DCF valuation
        """
        try:
            # Get WACC
            wacc_data = DCFModel.calculate_wacc(ticker)
            if "error" in wacc_data:
                return wacc_data
            
            wacc = wacc_override or wacc_data["wacc_decimal"]
            
            # Get projections
            projections = DCFModel.project_financials(
                ticker, projection_years, revenue_growth_rates, operating_margin_targets
            )
            if "error" in projections:
                return projections
            
            # Get historical for current data
            historical = DCFModel.get_historical_financials(ticker, 1)
            if "error" in historical:
                return historical
            
            terminal_growth = terminal_growth_rate or DCFModel.DEFAULT_TERMINAL_GROWTH
            
            # Calculate PV of projected FCFs
            pv_fcfs = []
            total_pv_fcf = 0
            
            for i, fcf in enumerate(projections["free_cash_flow"]):
                discount_factor = (1 + wacc) ** (i + 1)
                pv = fcf / discount_factor
                pv_fcfs.append(round(pv, 0))
                total_pv_fcf += pv
            
            # Calculate Terminal Value
            final_fcf = projections["free_cash_flow"][-1]
            terminal_value = (final_fcf * (1 + terminal_growth)) / (wacc - terminal_growth)
            
            # PV of Terminal Value
            pv_terminal = terminal_value / ((1 + wacc) ** projection_years)
            
            # Enterprise Value
            enterprise_value = total_pv_fcf + pv_terminal
            
            # Equity Value
            net_debt = historical.get("total_debt", 0) - historical.get("total_cash", 0)
            equity_value = enterprise_value - net_debt
            
            # Per Share Value
            shares_outstanding = historical.get("shares_outstanding", 1)
            if shares_outstanding and shares_outstanding > 0:
                intrinsic_value_per_share = equity_value / shares_outstanding
            else:
                intrinsic_value_per_share = 0
            
            # Current price comparison
            current_price = historical.get("current_price", 0)
            if current_price and current_price > 0:
                upside = ((intrinsic_value_per_share - current_price) / current_price) * 100
            else:
                upside = 0
            
            return {
                "ticker": ticker,
                "company_name": historical.get("company_name", ticker),
                "valuation_date": datetime.now().strftime("%Y-%m-%d"),
                
                # Assumptions
                "assumptions": {
                    "wacc": round(wacc * 100, 2),
                    "terminal_growth_rate": round(terminal_growth * 100, 2),
                    "projection_years": projection_years,
                    "revenue_growth_rates": projections["revenue_growth"],
                    "operating_margins": projections["operating_margin"]
                },
                
                # WACC breakdown
                "wacc_components": wacc_data,
                
                # Projections
                "projections": {
                    "years": projections["years"],
                    "revenue": projections["revenue"],
                    "free_cash_flow": projections["free_cash_flow"],
                    "pv_free_cash_flow": pv_fcfs
                },
                
                # Valuation
                "valuation": {
                    "pv_of_fcfs": round(total_pv_fcf / 1e9, 2),  # In billions
                    "terminal_value": round(terminal_value / 1e9, 2),
                    "pv_of_terminal_value": round(pv_terminal / 1e9, 2),
                    "enterprise_value": round(enterprise_value / 1e9, 2),
                    "net_debt": round(net_debt / 1e9, 2),
                    "equity_value": round(equity_value / 1e9, 2),
                    "shares_outstanding": round(shares_outstanding / 1e9, 2),  # In billions
                    "intrinsic_value_per_share": round(intrinsic_value_per_share, 2),
                    "current_price": round(current_price, 2),
                    "upside_percent": round(upside, 1),
                    "valuation_status": "UNDERVALUED" if upside > 10 else ("OVERVALUED" if upside < -10 else "FAIRLY VALUED")
                }
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def sensitivity_analysis(
        ticker: str,
        wacc_range: Tuple[float, float] = (0.08, 0.14),
        growth_range: Tuple[float, float] = (0.015, 0.04),
        steps: int = 5
    ) -> Dict[str, Any]:
        """
        Run sensitivity analysis on WACC and terminal growth rate.
        
        Args:
            ticker: Stock ticker symbol
            wacc_range: (min_wacc, max_wacc) as decimals
            growth_range: (min_growth, max_growth) as decimals
            steps: Number of steps in each dimension
            
        Returns:
            Sensitivity matrix with intrinsic values
        """
        try:
            wacc_values = np.linspace(wacc_range[0], wacc_range[1], steps)
            growth_values = np.linspace(growth_range[0], growth_range[1], steps)
            
            # Get base projections (only once)
            projections = DCFModel.project_financials(ticker, 5)
            if "error" in projections:
                return projections
            
            historical = DCFModel.get_historical_financials(ticker, 1)
            if "error" in historical:
                return historical
            
            shares_outstanding = historical.get("shares_outstanding", 1)
            net_debt = historical.get("total_debt", 0) - historical.get("total_cash", 0)
            current_price = historical.get("current_price", 0)
            
            # Build sensitivity matrix
            matrix = []
            wacc_labels = [f"{w*100:.1f}%" for w in wacc_values]
            growth_labels = [f"{g*100:.1f}%" for g in growth_values]
            
            for wacc in wacc_values:
                row = []
                for growth in growth_values:
                    # Calculate PV of FCFs
                    pv_fcf = sum(
                        fcf / ((1 + wacc) ** (i + 1))
                        for i, fcf in enumerate(projections["free_cash_flow"])
                    )
                    
                    # Terminal Value
                    final_fcf = projections["free_cash_flow"][-1]
                    if wacc > growth:
                        tv = (final_fcf * (1 + growth)) / (wacc - growth)
                        pv_tv = tv / ((1 + wacc) ** 5)
                    else:
                        pv_tv = 0
                    
                    # Intrinsic value per share
                    ev = pv_fcf + pv_tv
                    equity = ev - net_debt
                    per_share = equity / shares_outstanding if shares_outstanding else 0
                    
                    row.append(round(per_share, 2))
                matrix.append(row)
            
            return {
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "wacc_values": wacc_labels,
                "growth_values": growth_labels,
                "matrix": matrix,
                "wacc_range": f"{wacc_range[0]*100:.1f}% - {wacc_range[1]*100:.1f}%",
                "growth_range": f"{growth_range[0]*100:.1f}% - {growth_range[1]*100:.1f}%"
            }
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def get_dcf_summary(ticker: str) -> str:
        """
        Get a formatted DCF summary for AI responses.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Formatted string summary
        """
        dcf = DCFModel.calculate_dcf(ticker)
        
        if "error" in dcf:
            return f"Error calculating DCF for {ticker}: {dcf['error']}"
        
        v = dcf["valuation"]
        a = dcf["assumptions"]
        w = dcf["wacc_components"]
        
        summary = f"""
DCF VALUATION FOR {ticker.upper()}
{'='*50}

ASSUMPTIONS:
├── Revenue Growth: {' → '.join([f"{g}%" for g in a['revenue_growth_rates']])}
├── Operating Margins: {' → '.join([f"{m}%" for m in a['operating_margins']])}
├── WACC: {a['wacc']}%
│   ├── Cost of Equity: {w['cost_of_equity']}% (Beta: {w['beta']})
│   └── Cost of Debt (after-tax): {w['cost_of_debt_after_tax']}%
└── Terminal Growth: {a['terminal_growth_rate']}%

VALUATION:
├── PV of FCF (Years 1-5): ${v['pv_of_fcfs']}B
├── PV of Terminal Value: ${v['pv_of_terminal_value']}B
├── Enterprise Value: ${v['enterprise_value']}B
├── Less: Net Debt: ${v['net_debt']}B
├── Equity Value: ${v['equity_value']}B
├── Shares Outstanding: {v['shares_outstanding']}B
└── INTRINSIC VALUE: ${v['intrinsic_value_per_share']}/share

VERDICT:
├── Current Price: ${v['current_price']}
├── Upside/Downside: {v['upside_percent']:+.1f}%
└── Status: {v['valuation_status']}
"""
        return summary

