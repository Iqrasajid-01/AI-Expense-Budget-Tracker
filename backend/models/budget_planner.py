"""
Budget model representing a budget in the system
"""
from backend.models import BaseModel
from typing import Dict, Any, Optional, List
from backend.services.utils import validate_budget_period, validate_budget_amount, validate_budget_type, sanitize_text


class BudgetPlanner(BaseModel):
    """
    Budget model class representing a budget in the system
    """

    def __init__(self, db_path: str = "database/budget_app.db"):
        super().__init__(db_path)

    def validate_period(self, start_date: str, end_date: str) -> tuple[bool, str]:
        """
        Validate budget period dates
        Returns (is_valid, error_message)
        """
        return validate_budget_period(start_date, end_date)

    def validate_amount(self, amount: Any) -> tuple[bool, str]:
        """
        Validate budget amount
        Returns (is_valid, error_message)
        """
        return validate_budget_amount(amount)

    def validate_type(self, budget_type: str) -> tuple[bool, str]:
        """
        Validate budget type
        Returns (is_valid, error_message)
        """
        return validate_budget_type(budget_type)

    def create(self, user_id: int, category_id: Optional[int], amount: float,
               period_start: str, period_end: str, budget_type: str = 'monthly') -> Optional[Dict[str, Any]]:
        """
        Create a new budget with validation
        """
        # Validate inputs
        is_valid, msg = self.validate_amount(amount)
        if not is_valid:
            raise ValueError(f"Invalid amount: {msg}")

        is_valid, msg = self.validate_period(period_start, period_end)
        if not is_valid:
            raise ValueError(f"Invalid period: {msg}")

        is_valid, msg = self.validate_type(budget_type)
        if not is_valid:
            raise ValueError(f"Invalid budget type: {msg}")

        query = """
        INSERT INTO budgets (user_id, category_id, amount, period_start, period_end, budget_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            budget_id = self.execute_insert(query, (user_id, category_id, amount, period_start, period_end, budget_type))
            return self.get_by_id(budget_id)
        except Exception:
            return None

    def get_by_id(self, budget_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a budget by ID
        """
        query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.id = ?
        """
        results = self.execute_query(query, (budget_id,))
        if results:
            return dict(results[0])
        return None

    def get_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all budgets for a user
        """
        query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ?
        ORDER BY b.period_start DESC
        """
        results = self.execute_query(query, (user_id,))
        return [dict(row) for row in results]

    def get_by_user_and_category(self, user_id: int, category_id: int) -> List[Dict[str, Any]]:
        """
        Get all budgets for a user in a specific category
        """
        query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.category_id = ?
        ORDER BY b.period_start DESC
        """
        results = self.execute_query(query, (user_id, category_id))
        return [dict(row) for row in results]

    def get_current_budgets(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all budgets that are currently active (period includes today)
        """
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.period_start <= ? AND b.period_end >= ?
        ORDER BY b.period_start DESC
        """
        results = self.execute_query(query, (user_id, today, today))
        return [dict(row) for row in results]

    def update(self, budget_id: int, **kwargs) -> bool:
        """
        Update a budget with provided fields
        """
        allowed_fields = {'amount', 'period_start', 'period_end', 'budget_type', 'category_id'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not update_fields:
            return False

        # Validate fields before updating
        for field, value in update_fields.items():
            if field == 'amount':
                is_valid, msg = self.validate_amount(value)
                if not is_valid:
                    raise ValueError(f"Invalid amount: {msg}")
            elif field in ['period_start', 'period_end']:
                # Need to validate period as a whole
                pass
            elif field == 'budget_type':
                is_valid, msg = self.validate_type(value)
                if not is_valid:
                    raise ValueError(f"Invalid budget type: {msg}")

        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [budget_id]

        query = f"UPDATE budgets SET {set_clause} WHERE id = ?"
        try:
            self.execute_update(query, values)
            return True
        except Exception:
            return False

    def delete(self, budget_id: int) -> bool:
        """
        Delete a budget by ID
        """
        query = "DELETE FROM budgets WHERE id = ?"
        try:
            self.execute_update(query, (budget_id,))
            return True
        except Exception:
            return False

    def get_budget_performance(self, budget_id: int) -> Dict[str, Any]:
        """
        Get performance metrics for a specific budget
        """
        budget = self.get_by_id(budget_id)
        if not budget:
            return {}

        # Calculate how much of the budget has been used based on transactions
        # This would typically be calculated based on transactions within the budget period
        # For now, we'll return a placeholder implementation
        return {
            'budget_id': budget_id,
            'allocated_amount': budget['amount'],
            'used_amount': budget['amount'] * 0.7,  # Placeholder: 70% used
            'remaining_amount': budget['amount'] * 0.3,  # Placeholder: 30% remaining
            'usage_percentage': 70.0  # Placeholder: 70% used
        }

    def get_category_budget_history(self, user_id: int, category_id: int) -> List[Dict[str, Any]]:
        """
        Get historical budget data for a category
        """
        query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.category_id = ?
        ORDER BY b.period_start DESC
        LIMIT 12  -- Last 12 budgets
        """
        results = self.execute_query(query, (user_id, category_id))
        return [dict(row) for row in results]