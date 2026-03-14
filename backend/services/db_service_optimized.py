"""
Optimized PostgreSQL Database Service with Connection Pooling
Provides fast database operations with connection reuse
"""
import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

# Connection pool - initialized once
_connection_pool = None


def get_connection_pool():
    """Get or create the connection pool"""
    global _connection_pool
    if _connection_pool is None:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            database_url = 'postgresql://neondb_owner:npg_4FBhJngN8SUL@ep-rapid-butterfly-addi5ohb-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
        
        # Create connection pool (min 2, max 10 connections)
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            dsn=database_url,
            sslmode='require'
        )
    return _connection_pool


@contextmanager
def get_db_connection():
    """Context manager for database connections (fast - uses pool)"""
    conn = None
    try:
        pool = get_connection_pool()
        conn = pool.getconn()
        yield conn
    finally:
        if conn:
            pool.putconn(conn)


class DBService:
    """
    Optimized Database Service with connection pooling
    """

    def __init__(self):
        # Initialize connection pool on first use
        get_connection_pool()

    def create_transaction(self, user_id: int, amount: float, date: str,
                          description: str, category: Optional[str] = None,
                          type: str = 'Expense') -> Optional[Dict[str, Any]]:
        """Create a new transaction"""
        category_id = None
        if category:
            category_id = self.get_category_id_by_name(category)

        query = """
        INSERT INTO transactions (user_id, amount, date, description, category_id, type)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id, amount, date, description, category_id, type))
                transaction_id = cursor.fetchone()[0]
                conn.commit()
                cursor.close()

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
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (transaction_id,))
            row = cursor.fetchone()
            cursor.close()

        return dict(row) if row else None

    def get_user_transactions(self, user_id: int, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transactions for a user with optional pagination"""
        query = """
        SELECT t.*, c.name as category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s
        ORDER BY t.date DESC, t.created_at DESC
        """
        
        if limit:
            query += f" LIMIT {int(limit)} OFFSET {int(offset)}"

        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            cursor.close()

        return [dict(row) for row in rows]

    def get_user_transactions_summary(self, user_id: int) -> Dict[str, Any]:
        """Get fast aggregated summary (single query)"""
        query = """
        SELECT 
            COUNT(*) as total_count,
            SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as total_expenses,
            SUM(CASE WHEN type = 'Income' THEN amount ELSE -amount END) as balance
        FROM transactions
        WHERE user_id = %s
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            cursor.close()

        return dict(row) if row else {'total_count': 0, 'total_income': 0, 'total_expenses': 0, 'balance': 0}

    def get_category_breakdown(self, user_id: int) -> List[Dict[str, Any]]:
        """Get category breakdown (single optimized query)"""
        query = """
        SELECT c.name as category, SUM(t.amount) as amount
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s AND t.type = 'Expense'
        GROUP BY c.id, c.name
        ORDER BY amount DESC
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            cursor.close()

        return [dict(row) for row in rows]

    def get_weekly_expenses(self, user_id: int, weeks: int = 4) -> List[Dict[str, Any]]:
        """Get weekly expenses using SQL aggregation (fast)"""
        query = """
        SELECT 
            DATE_TRUNC('week', date) as week_start,
            SUM(amount) as amount
        FROM transactions
        WHERE user_id = %s AND type = 'Expense'
        AND date >= CURRENT_DATE - INTERVAL '%s weeks'
        GROUP BY DATE_TRUNC('week', date)
        ORDER BY week_start DESC
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (user_id, weeks))
            rows = cursor.fetchall()
            cursor.close()

        return [dict(row) for row in rows]

    def get_monthly_expenses(self, user_id: int, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly expenses using SQL aggregation (fast)"""
        query = """
        SELECT 
            DATE_TRUNC('month', date) as month_start,
            SUM(amount) as amount
        FROM transactions
        WHERE user_id = %s AND type = 'Expense'
        AND date >= CURRENT_DATE - INTERVAL '%s months'
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY month_start DESC
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (user_id, months))
            rows = cursor.fetchall()
            cursor.close()

        return [dict(row) for row in rows]

    def update_transaction(self, transaction_id: int, amount: float = None, date: str = None,
                          description: str = None, category: str = None, type: str = None) -> bool:
        """Update a transaction"""
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
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
            return True
        except psycopg2.Error as e:
            print(f"Error updating transaction: {e}")
            return False

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        query = "DELETE FROM transactions WHERE id = %s"
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (transaction_id,))
                conn.commit()
                cursor.close()
            return True
        except psycopg2.Error as e:
            print(f"Error deleting transaction: {e}")
            return False

    def get_category_id_by_name(self, category_name: str) -> Optional[int]:
        """Get category ID by name, create if doesn't exist"""
        # First try to get existing category
        query = "SELECT id FROM categories WHERE LOWER(name) = LOWER(%s)"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (category_name,))
            row = cursor.fetchone()
            
            if row:
                cursor.close()
                return row[0]
            
            # Create new category
            cursor.execute(
                "INSERT INTO categories (name) VALUES (%s) RETURNING id",
                (category_name,)
            )
            category_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            
        return category_id

    def get_all_categories(self) -> List[str]:
        """Get all categories"""
        query = "SELECT name FROM categories ORDER BY name"
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
        
        return [row['name'] for row in rows]

    def get_recent_transactions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions (optimized for dashboard)"""
        return self.get_user_transactions(user_id, limit=limit)

    def search_transactions(self, user_id: int, query_text: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search transactions by description"""
        query = """
        SELECT t.*, c.name as category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s 
        AND (t.description ILIKE %s OR t.category ILIKE %s)
        ORDER BY t.date DESC
        LIMIT %s
        """
        search_pattern = f"%{query_text}%"
        
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (user_id, search_pattern, search_pattern, limit))
            rows = cursor.fetchall()
            cursor.close()
        
        return [dict(row) for row in rows]
