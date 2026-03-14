"""
Base model class for database operations
"""
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
import os


class BaseModel:
    """
    Base model class providing common database operations
    """

    def __init__(self, db_path: str = "database/budget_app.db"):
        self.db_path = db_path
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def get_db_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        return conn

    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT, UPDATE, or DELETE query and return affected rows"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT query and return the new ID"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid