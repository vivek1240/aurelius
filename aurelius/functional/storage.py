"""
Local Storage Utilities for Watchlists and Saved Research
Uses SQLite for lightweight persistence
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database connection and setup"""
    
    _instance = None
    _db_path = None
    
    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = None):
        if self._initialized:
            return
        
        # Default to user's home directory for persistent storage
        if db_path is None:
            home = Path.home()
            ikshvaku_dir = home / ".ikshvaku"
            ikshvaku_dir.mkdir(exist_ok=True)
            db_path = str(ikshvaku_dir / "ikshvaku_data.db")
        
        self._db_path = db_path
        self._init_database()
        self._initialized = True
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Watchlists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Watchlist items (stocks)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watchlist_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                added_price REAL,
                target_price REAL,
                notes TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
                UNIQUE(watchlist_id, ticker)
            )
        ''')
        
        # Research notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                note_type TEXT DEFAULT 'general',
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Price alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                target_price REAL NOT NULL,
                is_active INTEGER DEFAULT 1,
                triggered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                result_summary TEXT,
                full_result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default watchlist if none exists
        cursor.execute("SELECT COUNT(*) FROM watchlists")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO watchlists (name, description) VALUES (?, ?)",
                ("My Watchlist", "Default watchlist for tracking stocks")
            )
        
        conn.commit()
        conn.close()


class WatchlistManager:
    """Manage watchlists and watchlist items"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    # ==================== WATCHLIST OPERATIONS ====================
    
    def create_watchlist(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new watchlist"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO watchlists (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()
            watchlist_id = cursor.lastrowid
            return {
                "success": True,
                "id": watchlist_id,
                "name": name,
                "message": f"Watchlist '{name}' created successfully"
            }
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "message": f"Watchlist '{name}' already exists"
            }
        finally:
            conn.close()
    
    def get_all_watchlists(self) -> List[Dict[str, Any]]:
        """Get all watchlists"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT w.*, COUNT(wi.id) as stock_count 
            FROM watchlists w 
            LEFT JOIN watchlist_items wi ON w.id = wi.watchlist_id 
            GROUP BY w.id 
            ORDER BY w.updated_at DESC
        ''')
        
        watchlists = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return watchlists
    
    def get_watchlist(self, watchlist_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific watchlist with its items"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM watchlists WHERE id = ?", (watchlist_id,))
        watchlist = cursor.fetchone()
        
        if not watchlist:
            conn.close()
            return None
        
        cursor.execute(
            "SELECT * FROM watchlist_items WHERE watchlist_id = ? ORDER BY added_at DESC",
            (watchlist_id,)
        )
        items = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        result = dict(watchlist)
        result['items'] = items
        return result
    
    def delete_watchlist(self, watchlist_id: int) -> Dict[str, Any]:
        """Delete a watchlist"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM watchlists WHERE id = ?", (watchlist_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            return {"success": True, "message": "Watchlist deleted"}
        return {"success": False, "message": "Watchlist not found"}
    
    # ==================== WATCHLIST ITEM OPERATIONS ====================
    
    def add_to_watchlist(
        self, 
        ticker: str, 
        watchlist_id: int = 1,
        added_price: float = None,
        target_price: float = None,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Add a stock to a watchlist"""
        ticker = ticker.upper().strip()
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO watchlist_items (watchlist_id, ticker, added_price, target_price, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (watchlist_id, ticker, added_price, target_price, notes))
            
            # Update watchlist timestamp
            cursor.execute(
                "UPDATE watchlists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (watchlist_id,)
            )
            
            conn.commit()
            return {
                "success": True,
                "ticker": ticker,
                "message": f"{ticker} added to watchlist"
            }
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "message": f"{ticker} is already in this watchlist"
            }
        finally:
            conn.close()
    
    def remove_from_watchlist(self, ticker: str, watchlist_id: int = 1) -> Dict[str, Any]:
        """Remove a stock from a watchlist"""
        ticker = ticker.upper().strip()
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM watchlist_items WHERE watchlist_id = ? AND ticker = ?",
            (watchlist_id, ticker)
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            return {"success": True, "message": f"{ticker} removed from watchlist"}
        return {"success": False, "message": f"{ticker} not found in watchlist"}
    
    def update_watchlist_item(
        self,
        ticker: str,
        watchlist_id: int = 1,
        target_price: float = None,
        notes: str = None
    ) -> Dict[str, Any]:
        """Update a watchlist item"""
        ticker = ticker.upper().strip()
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if target_price is not None:
            updates.append("target_price = ?")
            params.append(target_price)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        
        if not updates:
            return {"success": False, "message": "No updates provided"}
        
        params.extend([watchlist_id, ticker])
        query = f"UPDATE watchlist_items SET {', '.join(updates)} WHERE watchlist_id = ? AND ticker = ?"
        
        cursor.execute(query, params)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            return {"success": True, "message": f"{ticker} updated"}
        return {"success": False, "message": f"{ticker} not found in watchlist"}
    
    def get_watchlist_items(self, watchlist_id: int = 1) -> List[Dict[str, Any]]:
        """Get all items in a watchlist"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM watchlist_items WHERE watchlist_id = ? ORDER BY added_at DESC",
            (watchlist_id,)
        )
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def is_in_watchlist(self, ticker: str, watchlist_id: int = 1) -> bool:
        """Check if a ticker is in a watchlist"""
        ticker = ticker.upper().strip()
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM watchlist_items WHERE watchlist_id = ? AND ticker = ?",
            (watchlist_id, ticker)
        )
        result = cursor.fetchone() is not None
        conn.close()
        return result


class ResearchManager:
    """Manage research notes and analysis history"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    # ==================== RESEARCH NOTES ====================
    
    def save_note(
        self,
        ticker: str,
        title: str,
        content: str,
        note_type: str = "general",
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Save a research note"""
        ticker = ticker.upper().strip()
        tags_str = json.dumps(tags) if tags else None
        
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO research_notes (ticker, title, content, note_type, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticker, title, content, note_type, tags_str))
        
        conn.commit()
        note_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "id": note_id,
            "message": f"Note saved for {ticker}"
        }
    
    def get_notes_for_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        """Get all notes for a specific ticker"""
        ticker = ticker.upper().strip()
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM research_notes WHERE ticker = ? ORDER BY created_at DESC",
            (ticker,)
        )
        notes = [dict(row) for row in cursor.fetchall()]
        
        # Parse tags
        for note in notes:
            if note.get('tags'):
                note['tags'] = json.loads(note['tags'])
        
        conn.close()
        return notes
    
    def get_all_notes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all research notes"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM research_notes ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        notes = [dict(row) for row in cursor.fetchall()]
        
        for note in notes:
            if note.get('tags'):
                note['tags'] = json.loads(note['tags'])
        
        conn.close()
        return notes
    
    def update_note(self, note_id: int, title: str = None, content: str = None) -> Dict[str, Any]:
        """Update a research note"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        updates = ["updated_at = CURRENT_TIMESTAMP"]
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        params.append(note_id)
        query = f"UPDATE research_notes SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            return {"success": True, "message": "Note updated"}
        return {"success": False, "message": "Note not found"}
    
    def delete_note(self, note_id: int) -> Dict[str, Any]:
        """Delete a research note"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM research_notes WHERE id = ?", (note_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            return {"success": True, "message": "Note deleted"}
        return {"success": False, "message": "Note not found"}
    
    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by content or title"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM research_notes 
            WHERE title LIKE ? OR content LIKE ? OR ticker LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return notes
    
    # ==================== ANALYSIS HISTORY ====================
    
    def save_analysis(
        self,
        ticker: str,
        analysis_type: str,
        result_summary: str,
        full_result: str = None
    ) -> Dict[str, Any]:
        """Save an analysis result"""
        ticker = ticker.upper().strip()
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history (ticker, analysis_type, result_summary, full_result)
            VALUES (?, ?, ?, ?)
        ''', (ticker, analysis_type, result_summary, full_result))
        
        conn.commit()
        analysis_id = cursor.lastrowid
        conn.close()
        
        return {"success": True, "id": analysis_id}
    
    def get_analysis_history(self, ticker: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get analysis history, optionally filtered by ticker"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        if ticker:
            ticker = ticker.upper().strip()
            cursor.execute(
                "SELECT * FROM analysis_history WHERE ticker = ? ORDER BY created_at DESC LIMIT ?",
                (ticker, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM analysis_history ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history


class AlertManager:
    """Manage price alerts"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_alert(
        self,
        ticker: str,
        target_price: float,
        alert_type: str = "above"  # "above" or "below"
    ) -> Dict[str, Any]:
        """Create a price alert"""
        ticker = ticker.upper().strip()
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO price_alerts (ticker, alert_type, target_price)
            VALUES (?, ?, ?)
        ''', (ticker, alert_type, target_price))
        
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "id": alert_id,
            "message": f"Alert created: {ticker} {alert_type} ${target_price}"
        }
    
    def get_active_alerts(self, ticker: str = None) -> List[Dict[str, Any]]:
        """Get active alerts"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        if ticker:
            ticker = ticker.upper().strip()
            cursor.execute(
                "SELECT * FROM price_alerts WHERE is_active = 1 AND ticker = ? ORDER BY created_at DESC",
                (ticker,)
            )
        else:
            cursor.execute(
                "SELECT * FROM price_alerts WHERE is_active = 1 ORDER BY created_at DESC"
            )
        
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return alerts
    
    def deactivate_alert(self, alert_id: int) -> Dict[str, Any]:
        """Deactivate an alert"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE price_alerts SET is_active = 0, triggered_at = CURRENT_TIMESTAMP WHERE id = ?",
            (alert_id,)
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            return {"success": True, "message": "Alert deactivated"}
        return {"success": False, "message": "Alert not found"}
    
    def delete_alert(self, alert_id: int) -> Dict[str, Any]:
        """Delete an alert"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM price_alerts WHERE id = ?", (alert_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            return {"success": True, "message": "Alert deleted"}
        return {"success": False, "message": "Alert not found"}


# Convenience functions for quick access
def get_watchlist_manager() -> WatchlistManager:
    """Get a WatchlistManager instance"""
    return WatchlistManager()

def get_research_manager() -> ResearchManager:
    """Get a ResearchManager instance"""
    return ResearchManager()

def get_alert_manager() -> AlertManager:
    """Get an AlertManager instance"""
    return AlertManager()

