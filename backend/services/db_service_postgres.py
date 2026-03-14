"""
PostgreSQL Database Service
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Optional, Any


class DBService:
    """
    Database service for PostgreSQL (Neon)
    """

    def __init__(self):
        pass

    def get_db_connection(self):
        """Get PostgreSQL database connection"""
        # Use environment variable if available (Vercel)
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            # Fallback to provided Neon connection string
            database_url = 'postgresql://neondb_owner:npg_4FBhJngN8SUL@ep-rapid-butterfly-addi5ohb-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
        
        try:
            conn = psycopg2.connect(database_url, sslmode='require')
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            print(f"Database URL: {database_url[:50]}...")
            raise

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
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, (user_id, amount, date, description, category_id, type))
            transaction_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            # Return the created transaction with category name
            return self.get_transaction_by_id(transaction_id)
        except psycopg2.Error as e:
            print(f"Error creating transaction: {e}")
            return None

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a transaction by ID"""
        query = """
        SELECT t.*, c.name as category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = %s
        """
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (transaction_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def get_user_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all transactions for a user"""
        query = """
        SELECT t.*, c.name as category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s
        ORDER BY t.date DESC, t.created_at DESC
        """
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in rows]

    def update_transaction(self, transaction_id: int, amount: float = None, date: str = None,
                          description: str = None, category: str = None, type: str = None) -> bool:
        """Update a transaction"""
        # Build update fields
        updates = []
        values = []

        if amount is not None:
            updates.append("amount = %s")
            values.append(amount)
        if date is not None:
            updates.append("date = %s")
            values.append(date)
        if description is not None:
            updates.append("description = %s")
            values.append(description)
        if type is not None:
            updates.append("type = %s")
            values.append(type)
        if category is not None:
            category_id = self.get_category_id_by_name(category)
            updates.append("category_id = %s")
            values.append(category_id)

        if not updates:
            return False

        values.append(transaction_id)
        query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = %s"

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            result = cursor.rowcount > 0
            cursor.close()
            conn.close()
            return result
        except psycopg2.Error as e:
            print(f"Error updating transaction: {e}")
            return False

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by ID"""
        query = "DELETE FROM transactions WHERE id = %s"
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (transaction_id,))
        conn.commit()
        result = cursor.rowcount > 0
        cursor.close()
        conn.close()
        return result

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        query = "SELECT * FROM categories ORDER BY name"
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_category_id_by_name(self, name: str) -> Optional[int]:
        """Get category ID by name"""
        query = "SELECT id FROM categories WHERE name = %s"
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (name,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return row[0]
        return None

    def get_user_budgets(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all budgets for a user"""
        query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = %s
        ORDER BY b.period_start DESC
        """
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_financial_summary(self, user_id: int, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get financial summary for a user"""
        query = """
        SELECT
            SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as total_expenses
        FROM transactions
        WHERE user_id = %s
        """
        params = [user_id]

        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)

        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        conn.close()

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
