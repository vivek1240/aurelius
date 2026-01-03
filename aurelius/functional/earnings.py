"""
Earnings Intelligence Utilities
Track earnings history, estimates, surprises, and analyst revisions
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import yfinance as yf
from ..data_source import YFinanceUtils


class EarningsIntel:
    """Utility class for earnings intelligence and analysis"""
    
    @staticmethod
    def get_earnings_history(ticker: str, quarters: int = 8) -> Dict[str, Any]:
        """
        Get historical earnings data (EPS actual vs estimate)
        
        Args:
            ticker: Stock ticker symbol
            quarters: Number of quarters of history
            
        Returns:
            Dictionary with earnings history data
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get earnings history
            earnings_hist = stock.earnings_history
            
            result = {
                "ticker": ticker,
                "quarters": [],
                "summary": {}
            }
            
            if earnings_hist is not None and not earnings_hist.empty:
                # Process earnings history
                for idx, row in earnings_hist.head(quarters).iterrows():
                    quarter_data = {
                        "date": idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx),
                        "eps_estimate": float(row.get('epsEstimate', 0)) if pd.notna(row.get('epsEstimate')) else None,
                        "eps_actual": float(row.get('epsActual', 0)) if pd.notna(row.get('epsActual')) else None,
                        "surprise": float(row.get('surprise', 0)) if pd.notna(row.get('surprise')) else None,
                        "surprise_pct": float(row.get('surprisePercent', 0)) if pd.notna(row.get('surprisePercent')) else None
                    }
                    result["quarters"].append(quarter_data)
                
                # Calculate summary stats
                surprises = [q["surprise_pct"] for q in result["quarters"] if q["surprise_pct"] is not None]
                beats = [s for s in surprises if s > 0]
                misses = [s for s in surprises if s < 0]
                
                result["summary"] = {
                    "total_quarters": len(result["quarters"]),
                    "beats": len(beats),
                    "misses": len(misses),
                    "meets": len(surprises) - len(beats) - len(misses),
                    "avg_surprise_pct": round(np.mean(surprises), 2) if surprises else 0,
                    "beat_rate": round(len(beats) / len(surprises) * 100, 1) if surprises else 0,
                    "consecutive_beats": EarningsIntel._count_consecutive_beats(surprises)
                }
            
            return result
            
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "quarters": [], "summary": {}}
    
    @staticmethod
    def _count_consecutive_beats(surprises: List[float]) -> int:
        """Count consecutive earnings beats from most recent"""
        count = 0
        for s in surprises:
            if s > 0:
                count += 1
            else:
                break
        return count
    
    @staticmethod
    def get_revenue_history(ticker: str, quarters: int = 8) -> Dict[str, Any]:
        """
        Get historical revenue data
        
        Args:
            ticker: Stock ticker symbol
            quarters: Number of quarters
            
        Returns:
            Dictionary with revenue history
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get quarterly financials
            quarterly = stock.quarterly_financials
            
            result = {
                "ticker": ticker,
                "quarters": [],
                "summary": {}
            }
            
            if quarterly is not None and not quarterly.empty:
                # Get revenue row
                if "Total Revenue" in quarterly.index:
                    revenue = quarterly.loc["Total Revenue"]
                    
                    for i, (date, value) in enumerate(revenue.items()):
                        if i >= quarters:
                            break
                        
                        # Calculate YoY growth if we have enough data
                        yoy_growth = None
                        if i + 4 < len(revenue):
                            prev_year_val = revenue.iloc[i + 4]
                            if prev_year_val and prev_year_val != 0:
                                yoy_growth = round(((value - prev_year_val) / prev_year_val) * 100, 2)
                        
                        result["quarters"].append({
                            "date": date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date),
                            "revenue": float(value) if pd.notna(value) else None,
                            "yoy_growth": yoy_growth
                        })
                
                # Summary
                revenues = [q["revenue"] for q in result["quarters"] if q["revenue"]]
                growths = [q["yoy_growth"] for q in result["quarters"] if q["yoy_growth"] is not None]
                
                result["summary"] = {
                    "latest_revenue": revenues[0] if revenues else None,
                    "avg_quarterly_revenue": round(np.mean(revenues), 0) if revenues else None,
                    "avg_yoy_growth": round(np.mean(growths), 2) if growths else None,
                    "revenue_trend": "growing" if growths and np.mean(growths) > 0 else "declining"
                }
            
            return result
            
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "quarters": [], "summary": {}}
    
    @staticmethod
    def get_next_earnings(ticker: str) -> Dict[str, Any]:
        """
        Get next earnings date and current estimates
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with next earnings info
        """
        try:
            stock = yf.Ticker(ticker)
            
            result = {
                "ticker": ticker,
                "next_earnings_date": None,
                "eps_estimate": None,
                "revenue_estimate": None,
                "days_until": None
            }
            
            # Get calendar
            calendar = stock.calendar
            
            if calendar is not None:
                if isinstance(calendar, pd.DataFrame):
                    if 'Earnings Date' in calendar.index:
                        earnings_dates = calendar.loc['Earnings Date']
                        if len(earnings_dates) > 0:
                            next_date = earnings_dates.iloc[0]
                            if pd.notna(next_date):
                                result["next_earnings_date"] = str(next_date)
                                
                                # Calculate days until
                                if hasattr(next_date, 'date'):
                                    days = (next_date.date() - datetime.now().date()).days
                                    result["days_until"] = max(0, days)
                elif isinstance(calendar, dict):
                    if 'Earnings Date' in calendar:
                        dates = calendar['Earnings Date']
                        if dates:
                            result["next_earnings_date"] = str(dates[0]) if isinstance(dates, list) else str(dates)
            
            # Get analyst estimates
            try:
                earnings_est = stock.earnings_estimate
                if earnings_est is not None and not earnings_est.empty:
                    if 'avg' in earnings_est.columns:
                        result["eps_estimate"] = float(earnings_est['avg'].iloc[0]) if pd.notna(earnings_est['avg'].iloc[0]) else None
            except:
                pass
            
            try:
                revenue_est = stock.revenue_estimate
                if revenue_est is not None and not revenue_est.empty:
                    if 'avg' in revenue_est.columns:
                        result["revenue_estimate"] = float(revenue_est['avg'].iloc[0]) if pd.notna(revenue_est['avg'].iloc[0]) else None
            except:
                pass
            
            return result
            
        except Exception as e:
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def get_analyst_estimates(ticker: str) -> Dict[str, Any]:
        """
        Get analyst estimates and recommendations
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with analyst data
        """
        try:
            stock = yf.Ticker(ticker)
            
            result = {
                "ticker": ticker,
                "eps_estimates": {},
                "revenue_estimates": {},
                "recommendations": {},
                "price_targets": {}
            }
            
            # EPS Estimates
            try:
                eps_est = stock.earnings_estimate
                if eps_est is not None and not eps_est.empty:
                    for period in eps_est.index:
                        result["eps_estimates"][str(period)] = {
                            "avg": float(eps_est.loc[period, 'avg']) if 'avg' in eps_est.columns and pd.notna(eps_est.loc[period, 'avg']) else None,
                            "low": float(eps_est.loc[period, 'low']) if 'low' in eps_est.columns and pd.notna(eps_est.loc[period, 'low']) else None,
                            "high": float(eps_est.loc[period, 'high']) if 'high' in eps_est.columns and pd.notna(eps_est.loc[period, 'high']) else None,
                            "num_analysts": int(eps_est.loc[period, 'numberOfAnalysts']) if 'numberOfAnalysts' in eps_est.columns and pd.notna(eps_est.loc[period, 'numberOfAnalysts']) else None
                        }
            except:
                pass
            
            # Revenue Estimates
            try:
                rev_est = stock.revenue_estimate
                if rev_est is not None and not rev_est.empty:
                    for period in rev_est.index:
                        result["revenue_estimates"][str(period)] = {
                            "avg": float(rev_est.loc[period, 'avg']) if 'avg' in rev_est.columns and pd.notna(rev_est.loc[period, 'avg']) else None,
                            "low": float(rev_est.loc[period, 'low']) if 'low' in rev_est.columns and pd.notna(rev_est.loc[period, 'low']) else None,
                            "high": float(rev_est.loc[period, 'high']) if 'high' in rev_est.columns and pd.notna(rev_est.loc[period, 'high']) else None,
                        }
            except:
                pass
            
            # Recommendations
            try:
                recs = stock.recommendations
                if recs is not None and not recs.empty:
                    # Get latest recommendations summary
                    recent = recs.tail(10)
                    if 'To Grade' in recent.columns:
                        grades = recent['To Grade'].value_counts().to_dict()
                        result["recommendations"] = {
                            "grades": grades,
                            "total_analysts": len(recent)
                        }
            except:
                pass
            
            # Price Targets
            try:
                info = stock.info
                result["price_targets"] = {
                    "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "target_low": info.get("targetLowPrice"),
                    "target_mean": info.get("targetMeanPrice"),
                    "target_high": info.get("targetHighPrice"),
                    "num_analysts": info.get("numberOfAnalystOpinions")
                }
                
                # Calculate upside/downside
                if result["price_targets"]["current_price"] and result["price_targets"]["target_mean"]:
                    current = result["price_targets"]["current_price"]
                    target = result["price_targets"]["target_mean"]
                    result["price_targets"]["upside_pct"] = round(((target - current) / current) * 100, 2)
            except:
                pass
            
            return result
            
        except Exception as e:
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def get_earnings_surprise_streak(ticker: str) -> Dict[str, Any]:
        """
        Analyze earnings surprise streak and patterns
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with streak analysis
        """
        history = EarningsIntel.get_earnings_history(ticker, quarters=12)
        
        if "error" in history or not history.get("quarters"):
            return {"ticker": ticker, "error": "No earnings history available"}
        
        surprises = []
        for q in history["quarters"]:
            if q.get("surprise_pct") is not None:
                surprises.append({
                    "date": q["date"],
                    "surprise_pct": q["surprise_pct"],
                    "beat": q["surprise_pct"] > 0
                })
        
        if not surprises:
            return {"ticker": ticker, "error": "No surprise data"}
        
        # Current streak
        current_streak = 0
        streak_type = None
        for s in surprises:
            if streak_type is None:
                streak_type = "beat" if s["beat"] else "miss"
                current_streak = 1
            elif (streak_type == "beat" and s["beat"]) or (streak_type == "miss" and not s["beat"]):
                current_streak += 1
            else:
                break
        
        # Best and worst surprises
        surprise_values = [s["surprise_pct"] for s in surprises]
        
        return {
            "ticker": ticker,
            "current_streak": current_streak,
            "streak_type": streak_type,
            "best_surprise": {
                "value": max(surprise_values),
                "date": surprises[surprise_values.index(max(surprise_values))]["date"]
            },
            "worst_surprise": {
                "value": min(surprise_values),
                "date": surprises[surprise_values.index(min(surprise_values))]["date"]
            },
            "avg_beat_magnitude": round(np.mean([s for s in surprise_values if s > 0]), 2) if any(s > 0 for s in surprise_values) else 0,
            "avg_miss_magnitude": round(np.mean([s for s in surprise_values if s < 0]), 2) if any(s < 0 for s in surprise_values) else 0
        }
    
    @staticmethod
    def get_full_earnings_report(ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive earnings report combining all data
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Complete earnings intelligence report
        """
        return {
            "ticker": ticker,
            "generated_at": datetime.now().isoformat(),
            "earnings_history": EarningsIntel.get_earnings_history(ticker),
            "revenue_history": EarningsIntel.get_revenue_history(ticker),
            "next_earnings": EarningsIntel.get_next_earnings(ticker),
            "analyst_estimates": EarningsIntel.get_analyst_estimates(ticker),
            "streak_analysis": EarningsIntel.get_earnings_surprise_streak(ticker)
        }

