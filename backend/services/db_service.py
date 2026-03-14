"""
Database service for common operations
Updated to work with the new database schema
"""
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import os


class DBService:
    """
    Database service providing common operations for the budget application
    """

    def __init__(self):
        # Use the correct database path (same as setup_db.py)
        # Check if running on Vercel (serverless environment)
        if os.environ.get('VERCEL'):
            # Use /tmp directory on Vercel (writable)
            db_dir = '/tmp/budget_tracker'
            os.makedirs(db_dir, exist_ok=True)
            self.db_path = os.path.join(db_dir, 'budget_tracker.db')
        else:
            # Local development
            db_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
            os.makedirs(db_dir, exist_ok=True)
            self.db_path = os.path.join(db_dir, 'budget_tracker.db')

    def get_db_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_transaction(self, user_id: int, amount: float, date: str,
                          description: str, category: Optional[str] = None,
                          type: str = 'Expense') -> Optional[Dict[str, Any]]:
        """Create a new transaction"""
        # Get category ID if category name is provided
        category_id = None
        if category:
            category_id = self.get_category_id_by_name(category)

        query = """
        INSERT INTO transactions (user_id, amount, date, description, category_id, type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id, amount, date, description, category_id, type))
                transaction_id = cursor.lastrowid
                conn.commit()

                # Return the created transaction with category name
                return self.get_transaction_by_id(transaction_id)
        except sqlite3.Error as e:
            print(f"Error creating transaction: {e}")
            return None

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a transaction by ID"""
        query = """
        SELECT t.*, c.name as category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (transaction_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_user_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all transactions for a user"""
        query = """
        SELECT t.*, c.name as category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC, t.created_at DESC
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_transaction(self, transaction_id: int, amount: float = None, date: str = None,
                          description: str = None, category: str = None, type: str = None) -> bool:
        """Update a transaction"""
        # Build update fields
        updates = []
        values = []
        
        if amount is not None:
            updates.append("amount = ?")
            values.append(amount)
        if date is not None:
            updates.append("date = ?")
            values.append(date)
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if type is not None:
            updates.append("type = ?")
            values.append(type)
        if category is not None:
            category_id = self.get_category_id_by_name(category)
            updates.append("category_id = ?")
            values.append(category_id)
        
        if not updates:
            return False
        
        values.append(transaction_id)
        query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ?"
        
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating transaction: {e}")
            return False

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by ID"""
        query = "DELETE FROM transactions WHERE id = ?"
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        query = "SELECT * FROM categories ORDER BY name"
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_category_id_by_name(self, name: str) -> Optional[int]:
        """Get category ID by name"""
        query = "SELECT id FROM categories WHERE name = ?"
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None

    def get_user_budgets(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all budgets for a user"""
        query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ?
        ORDER BY b.period_start DESC
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_financial_summary(self, user_id: int, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get financial summary for a user"""
        query = """
        SELECT
            SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as total_expenses
        FROM transactions
        WHERE user_id = ?
        """
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()

            total_income = row['total_income'] or 0
            total_expenses = row['total_expenses'] or 0
            savings_rate = (total_income - total_expenses) / total_income * 100 if total_income > 0 else 0

            return {
                'summary': {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'savings_rate': savings_rate
                }
            }
