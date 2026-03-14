"""
Category model representing a category in the system
"""
from backend.models import BaseModel
from typing import Dict, Any, Optional, List
from backend.services.utils import validate_category_name, validate_color_code, sanitize_text


class CategoryManager(BaseModel):
    """
    Category model class representing a category in the system
    """

    def __init__(self, db_path: str = "database/budget_app.db"):
        super().__init__(db_path)

    def validate_name(self, name: str) -> tuple[bool, str]:
        """
        Validate category name
        Returns (is_valid, error_message)
        """
        return validate_category_name(name)

    def validate_color_code(self, color_code: str) -> tuple[bool, str]:
        """
        Validate color code
        Returns (is_valid, error_message)
        """
        return validate_color_code(color_code)

    def create(self, name: str, description: str = None, color_code: str = '#000000') -> Optional[Dict[str, Any]]:
        """
        Create a new category with validation
        """
        # Validate inputs
        is_valid, msg = self.validate_name(name)
        if not is_valid:
            raise ValueError(f"Invalid name: {msg}")

        is_valid, msg = self.validate_color_code(color_code)
        if not is_valid:
            raise ValueError(f"Invalid color code: {msg}")

        # Sanitize inputs
        name = sanitize_text(name)
        description = sanitize_text(description) if description else None

        query = """
        INSERT INTO categories (name, description, color_code)
        VALUES (?, ?, ?)
        """
        try:
            category_id = self.execute_insert(query, (name, description, color_code))
            return self.get_by_id(category_id)
        except Exception:
            return None

    def get_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a category by ID
        """
        query = "SELECT * FROM categories WHERE id = ?"
        results = self.execute_query(query, (category_id,))
        if results:
            return dict(results[0])
        return None

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a category by name
        """
        query = "SELECT * FROM categories WHERE name = ?"
        results = self.execute_query(query, (name,))
        if results:
            return dict(results[0])
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all categories
        """
        query = "SELECT * FROM categories ORDER BY name"
        results = self.execute_query(query)
        return [dict(row) for row in results]

    def get_active(self) -> List[Dict[str, Any]]:
        """
        Get all active categories
        """
        query = "SELECT * FROM categories WHERE is_active = 1 ORDER BY name"
        results = self.execute_query(query)
        return [dict(row) for row in results]

    def update(self, category_id: int, **kwargs) -> bool:
        """
        Update a category with provided fields
        """
        allowed_fields = {'name', 'description', 'color_code', 'is_active'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not update_fields:
            return False

        # Validate fields before updating
        for field, value in update_fields.items():
            if field == 'name':
                is_valid, msg = self.validate_name(value)
                if not is_valid:
                    raise ValueError(f"Invalid name: {msg}")
            elif field == 'color_code':
                is_valid, msg = self.validate_color_code(value)
                if not is_valid:
                    raise ValueError(f"Invalid color code: {msg}")

        # Sanitize text fields
        if 'name' in update_fields:
            update_fields['name'] = sanitize_text(update_fields['name'])
        if 'description' in update_fields and update_fields['description']:
            update_fields['description'] = sanitize_text(update_fields['description'])

        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [category_id]

        query = f"UPDATE categories SET {set_clause} WHERE id = ?"
        try:
            self.execute_update(query, values)
            return True
        except Exception:
            return False

    def delete(self, category_id: int) -> bool:
        """
        Delete a category by ID (soft delete by setting is_active to 0)
        """
        query = "UPDATE categories SET is_active = 0 WHERE id = ?"
        try:
            self.execute_update(query, (category_id,))
            return True
        except Exception:
            return False

    def get_expense_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories that are typically used for expenses
        """
        # In our system, all categories except 'Salary' and 'Investment' are typically expenses
        query = "SELECT * FROM categories WHERE name NOT IN ('Salary', 'Investment') AND is_active = 1 ORDER BY name"
        results = self.execute_query(query)
        return [dict(row) for row in results]

    def get_income_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories that are typically used for income
        """
        query = "SELECT * FROM categories WHERE name IN ('Salary', 'Investment') AND is_active = 1 ORDER BY name"
        results = self.execute_query(query)
        return [dict(row) for row in results]

    def search_categories(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search categories by name or description
        """
        query = "SELECT * FROM categories WHERE (name LIKE ? OR description LIKE ?) AND is_active = 1 ORDER BY name"
        search_pattern = f"%{search_term}%"
        results = self.execute_query(query, (search_pattern, search_pattern))
        return [dict(row) for row in results]