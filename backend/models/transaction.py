"""
Transaction model representing a financial transaction in the system
"""
from backend.models import BaseModel
from typing import Dict, Any, Optional, List
from backend.services.utils import validate_amount, validate_date, validate_transaction_type, sanitize_description


class Transaction(BaseModel):
    """
    Transaction model class representing a financial transaction in the system
    """

    def __init__(self, db_path: str = "database/budget_app.db"):
        super().__init__(db_path)

    def validate_amount(self, amount: Any) -> tuple[bool, str]:
        """
        Validate transaction amount
        Returns (is_valid, error_message)
        """
        return validate_amount(amount)

    def validate_date(self, date: str) -> tuple[bool, str]:
        """
        Validate transaction date
        Returns (is_valid, error_message)
        """
        return validate_date(date)

    def validate_type(self, trans_type: str) -> tuple[bool, str]:
        """
        Validate transaction type (income or expense)
        Returns (is_valid, error_message)
        """
        return validate_transaction_type(trans_type)

    def create(self, user_id: int, amount: float, date: str, description: str,
               category_id: Optional[int] = None, type: str = 'expense') -> Optional[Dict[str, Any]]:
        """
        Create a new transaction with validation
        """
        # Validate inputs
        is_valid, msg = self.validate_amount(amount)
        if not is_valid:
            raise ValueError(f"Invalid amount: {msg}")

        is_valid, msg = self.validate_date(date)
        if not is_valid:
            raise ValueError(f"Invalid date: {msg}")

        is_valid, msg = self.validate_type(type)
        if not is_valid:
            raise ValueError(f"Invalid type: {msg}")

        # Sanitize description
        description = sanitize_description(description)

        query = """
        INSERT INTO transactions (user_id, amount, date, description, category_id, type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            transaction_id = self.execute_insert(query, (user_id, amount, date, description, category_id, type))
            return self.get_by_id(transaction_id)
        except Exception:
            return None

    def get_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a transaction by ID
        """
        query = """
        SELECT t.*, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
        """
        results = self.execute_query(query, (transaction_id,))
        if results:
            return dict(results[0])
        return None

    def get_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all transactions for a user
        """
        query = """
        SELECT t.*, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC, t.created_at DESC
        """
        results = self.execute_query(query, (user_id,))
        return [dict(row) for row in results]

    def get_by_user_and_date_range(self, user_id: int, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get transactions for a user within a date range
        """
        query = """
        SELECT t.*, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.date BETWEEN ? AND ?
        ORDER BY t.date DESC, t.created_at DESC
        """
        results = self.execute_query(query, (user_id, start_date, end_date))
        return [dict(row) for row in results]

    def get_by_type(self, user_id: int, trans_type: str) -> List[Dict[str, Any]]:
        """
        Get transactions of a specific type for a user
        """
        query = """
        SELECT t.*, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.type = ?
        ORDER BY t.date DESC, t.created_at DESC
        """
        results = self.execute_query(query, (user_id, trans_type))
        return [dict(row) for row in results]

    def update(self, transaction_id: int, **kwargs) -> bool:
        """
        Update a transaction with provided fields
        """
        allowed_fields = {'amount', 'date', 'description', 'category_id', 'type'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not update_fields:
            return False

        # Validate fields before updating
        for field, value in update_fields.items():
            if field == 'amount':
                is_valid, msg = self.validate_amount(value)
                if not is_valid:
                    raise ValueError(f"Invalid amount: {msg}")
            elif field == 'date':
                is_valid, msg = self.validate_date(value)
                if not is_valid:
                    raise ValueError(f"Invalid date: {msg}")
            elif field == 'type':
                is_valid, msg = self.validate_type(value)
                if not is_valid:
                    raise ValueError(f"Invalid type: {msg}")
            elif field == 'description':
                update_fields[field] = sanitize_description(str(value))

        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [transaction_id]

        query = f"UPDATE transactions SET {set_clause} WHERE id = ?"
        try:
            self.execute_update(query, values)
            return True
        except Exception:
            return False

    def delete(self, transaction_id: int) -> bool:
        """
        Delete a transaction by ID
        """
        query = "DELETE FROM transactions WHERE id = ?"
        try:
            self.execute_update(query, (transaction_id,))
            return True
        except Exception:
            return False

    def get_total_by_type(self, user_id: int, trans_type: str, start_date: str = None, end_date: str = None) -> float:
        """
        Get total amount for a specific transaction type within an optional date range
        """
        query = "SELECT SUM(amount) as total FROM transactions WHERE user_id = ? AND type = ?"
        params = [user_id, trans_type]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        results = self.execute_query(query, tuple(params))
        if results and results[0]['total'] is not None:
            return float(results[0]['total'])
        return 0.0

    def get_transactions_by_category(self, user_id: int, category_id: int) -> List[Dict[str, Any]]:
        """
        Get all transactions for a user in a specific category
        """
        query = """
        SELECT t.*, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.category_id = ?
        ORDER BY t.date DESC, t.created_at DESC
        """
        results = self.execute_query(query, (user_id, category_id))
        return [dict(row) for row in results]