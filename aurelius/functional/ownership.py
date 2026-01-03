"""
Ownership Analysis Utilities for Ikshvaku

Provides institutional ownership, insider trading, and ownership breakdown analysis.
"""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import yfinance as yf


class OwnershipIntel:
    """Utilities for ownership analysis."""
    
    @staticmethod
    def get_ownership_breakdown(ticker: str) -> Dict[str, Any]:
        """
        Get ownership breakdown showing institutional, insider, and public ownership.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with ownership percentages and counts
        """
        try:
            stock = yf.Ticker(ticker)
            major_holders = stock.major_holders
            
            if major_holders is None or major_holders.empty:
                return {"error": f"No ownership data available for {ticker}"}
            
            # Parse the major holders data - 'Breakdown' is the index
            breakdown = {}
            for idx, row in major_holders.iterrows():
                key = idx  # Index is the breakdown type
                value = row['Value']
                breakdown[key] = value
            
            return {
                "ticker": ticker,
                "insiders_percent": breakdown.get('insidersPercentHeld', 0) * 100,
                "institutions_percent": breakdown.get('institutionsPercentHeld', 0) * 100,
                "institutions_float_percent": breakdown.get('institutionsFloatPercentHeld', 0) * 100,
                "institutions_count": int(breakdown.get('institutionsCount', 0)),
                "public_percent": max(0, (1 - breakdown.get('insidersPercentHeld', 0) - breakdown.get('institutionsPercentHeld', 0)) * 100),
                "retrieved_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def get_institutional_holders(ticker: str, top_n: int = 10) -> pd.DataFrame:
        """
        Get top institutional holders for a stock.
        
        Args:
            ticker: Stock ticker symbol
            top_n: Number of top holders to return
            
        Returns:
            DataFrame with institutional holder details
        """
        try:
            stock = yf.Ticker(ticker)
            inst_holders = stock.institutional_holders
            
            if inst_holders is None or inst_holders.empty:
                return pd.DataFrame()
            
            # Clean up the data
            df = inst_holders.head(top_n).copy()
            
            # Format date if present
            if 'Date Reported' in df.columns:
                df['Date Reported'] = pd.to_datetime(df['Date Reported']).dt.strftime('%Y-%m-%d')
            
            # Format value as billions
            if 'Value' in df.columns:
                df['Value (B)'] = df['Value'] / 1e9
            
            # Format pctChange as percentage
            if 'pctChange' in df.columns:
                df['Change %'] = df['pctChange'] * 100
            
            return df
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
    
    @staticmethod
    def get_mutual_fund_holders(ticker: str, top_n: int = 10) -> pd.DataFrame:
        """
        Get top mutual fund holders for a stock.
        
        Args:
            ticker: Stock ticker symbol
            top_n: Number of top holders to return
            
        Returns:
            DataFrame with mutual fund holder details
        """
        try:
            stock = yf.Ticker(ticker)
            mf_holders = stock.mutualfund_holders
            
            if mf_holders is None or mf_holders.empty:
                return pd.DataFrame()
            
            df = mf_holders.head(top_n).copy()
            
            # Format date if present
            if 'Date Reported' in df.columns:
                df['Date Reported'] = pd.to_datetime(df['Date Reported']).dt.strftime('%Y-%m-%d')
            
            # Format value as billions
            if 'Value' in df.columns:
                df['Value (B)'] = df['Value'] / 1e9
            
            # Format pctChange as percentage
            if 'pctChange' in df.columns:
                df['Change %'] = df['pctChange'] * 100
            
            return df
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
    
    @staticmethod
    def get_insider_transactions(ticker: str, limit: int = 20) -> pd.DataFrame:
        """
        Get recent insider transactions.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of transactions to return
            
        Returns:
            DataFrame with insider transaction details
        """
        try:
            stock = yf.Ticker(ticker)
            transactions = stock.insider_transactions
            
            if transactions is None or transactions.empty:
                return pd.DataFrame()
            
            df = transactions.head(limit).copy()
            
            # Format Start Date if present
            if 'Start Date' in df.columns:
                df['Start Date'] = pd.to_datetime(df['Start Date']).dt.strftime('%Y-%m-%d')
            
            return df
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
    
    @staticmethod
    def get_insider_summary(ticker: str) -> Dict[str, Any]:
        """
        Get a summary of insider trading activity.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with insider trading summary
        """
        try:
            stock = yf.Ticker(ticker)
            purchases = stock.insider_purchases
            
            if purchases is None or purchases.empty:
                return {"error": f"No insider data available for {ticker}"}
            
            # Parse the summary
            summary = {}
            for _, row in purchases.iterrows():
                key = row['Insider Purchases Last 6m']
                shares = row.get('Shares', 0)
                trans = row.get('Trans', 0)
                
                if key == 'Purchases':
                    summary['purchases_shares'] = float(shares) if pd.notna(shares) else 0
                    summary['purchases_count'] = int(trans) if pd.notna(trans) else 0
                elif key == 'Sales':
                    summary['sales_shares'] = float(shares) if pd.notna(shares) else 0
                    summary['sales_count'] = int(trans) if pd.notna(trans) else 0
                elif key == 'Net Shares Purchased (Sold)':
                    summary['net_shares'] = float(shares) if pd.notna(shares) else 0
                elif key == 'Total Insider Shares Held':
                    summary['total_insider_shares'] = float(shares) if pd.notna(shares) else 0
                elif key == '% Net Shares Purchased (Sold)':
                    summary['net_pct_change'] = float(shares) * 100 if pd.notna(shares) else 0
            
            # Determine sentiment
            net = summary.get('net_shares', 0)
            if net > 0:
                summary['sentiment'] = 'Bullish (Net Buying)'
            elif net < 0:
                summary['sentiment'] = 'Bearish (Net Selling)'
            else:
                summary['sentiment'] = 'Neutral'
            
            summary['ticker'] = ticker
            summary['period'] = 'Last 6 Months'
            
            return summary
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def get_ownership_comparison(tickers: List[str]) -> pd.DataFrame:
        """
        Compare ownership structure across multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            DataFrame comparing ownership across stocks
        """
        data = []
        
        for ticker in tickers:
            try:
                breakdown = OwnershipIntel.get_ownership_breakdown(ticker)
                if 'error' not in breakdown:
                    data.append({
                        'Ticker': ticker,
                        'Insider %': round(breakdown.get('insiders_percent', 0), 2),
                        'Institution %': round(breakdown.get('institutions_percent', 0), 2),
                        'Public %': round(breakdown.get('public_percent', 0), 2),
                        'Institution Count': breakdown.get('institutions_count', 0)
                    })
                else:
                    data.append({
                        'Ticker': ticker,
                        'Insider %': 'N/A',
                        'Institution %': 'N/A',
                        'Public %': 'N/A',
                        'Institution Count': 'N/A'
                    })
            except Exception:
                data.append({
                    'Ticker': ticker,
                    'Insider %': 'Error',
                    'Institution %': 'Error',
                    'Public %': 'Error',
                    'Institution Count': 'Error'
                })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def get_full_ownership_report(ticker: str) -> Dict[str, Any]:
        """
        Generate a comprehensive ownership report for a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with complete ownership analysis
        """
        report = {
            "ticker": ticker,
            "generated_at": datetime.now().isoformat()
        }
        
        # Get ownership breakdown
        report['breakdown'] = OwnershipIntel.get_ownership_breakdown(ticker)
        
        # Get insider summary
        report['insider_summary'] = OwnershipIntel.get_insider_summary(ticker)
        
        # Get top institutional holders
        inst_holders = OwnershipIntel.get_institutional_holders(ticker, top_n=5)
        if not inst_holders.empty and 'error' not in inst_holders.columns:
            report['top_institutions'] = inst_holders[['Holder', 'Value (B)', 'Change %']].to_dict('records') if 'Holder' in inst_holders.columns else []
        else:
            report['top_institutions'] = []
        
        # Get top mutual fund holders
        mf_holders = OwnershipIntel.get_mutual_fund_holders(ticker, top_n=5)
        if not mf_holders.empty and 'error' not in mf_holders.columns:
            report['top_mutual_funds'] = mf_holders[['Holder', 'Value (B)', 'Change %']].to_dict('records') if 'Holder' in mf_holders.columns else []
        else:
            report['top_mutual_funds'] = []
        
        return report

