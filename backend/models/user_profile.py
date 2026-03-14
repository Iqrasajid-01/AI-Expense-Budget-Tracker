"""
UserProfile model representing a user profile in the system
"""
from backend.models import BaseModel
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash
from backend.services.utils import validate_email, validate_password_strength, sanitize_text


class UserProfile(BaseModel):
    """
    UserProfile model class representing a user profile in the system
    """

    def __init__(self, db_path: str = "database/budget_app.db"):
        super().__init__(db_path)

    def validate_username(self, username: str) -> tuple[bool, str]:
        """
        Validate username
        Returns (is_valid, error_message)
        """
        if not username or len(username.strip()) == 0:
            return False, "Username cannot be empty"
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        if len(username) > 50:
            return False, "Username cannot exceed 50 characters"
        # Check for valid characters (letters, numbers, underscores, hyphens)
        if not username.replace('_', '').replace('-', '').isalnum():
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        return True, ""

    def validate_email(self, email: str) -> tuple[bool, str]:
        """
        Validate email
        Returns (is_valid, error_message)
        """
        return validate_email(email), "" if validate_email(email) else "Invalid email format"

    def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password
        Returns (is_valid, error_message)
        """
        return validate_password_strength(password)

    def create(self, username: str, email: str, password: str, first_name: str = None,
               last_name: str = None, currency: str = 'USD', timezone: str = 'UTC') -> Optional[Dict[str, Any]]:
        """
        Create a new user profile with validation
        """
        # Validate inputs
        is_valid, msg = self.validate_username(username)
        if not is_valid:
            raise ValueError(f"Invalid username: {msg}")

        is_valid, msg = self.validate_email(email)
        if not is_valid:
            raise ValueError(f"Invalid email: {msg}")

        is_valid, msg = self.validate_password(password)
        if not is_valid:
            raise ValueError(f"Invalid password: {msg}")

        # Sanitize inputs
        username = sanitize_text(username)
        email = sanitize_text(email)
        first_name = sanitize_text(first_name) if first_name else None
        last_name = sanitize_text(last_name) if last_name else None

        password_hash = generate_password_hash(password)
        query = """
        INSERT INTO user_profiles (username, email, password_hash, first_name, last_name, currency, timezone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            user_id = self.execute_insert(query, (username, email, password_hash, first_name, last_name, currency, timezone))
            return self.get_by_id(user_id)
        except Exception:
            return None

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user profile by ID
        """
        query = "SELECT * FROM user_profiles WHERE id = ?"
        results = self.execute_query(query, (user_id,))
        if results:
            return dict(results[0])
        return None

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a user profile by username
        """
        query = "SELECT * FROM user_profiles WHERE username = ?"
        results = self.execute_query(query, (username,))
        if results:
            return dict(results[0])
        return None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user profile by email
        """
        query = "SELECT * FROM user_profiles WHERE email = ?"
        results = self.execute_query(query, (email,))
        if results:
            return dict(results[0])
        return None

    def update(self, user_id: int, **kwargs) -> bool:
        """
        Update a user profile with provided fields
        """
        allowed_fields = {'username', 'email', 'first_name', 'last_name', 'currency', 'timezone'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not update_fields:
            return False

        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [user_id]

        query = f"UPDATE user_profiles SET {set_clause} WHERE id = ?"
        try:
            self.execute_update(query, values)
            return True
        except Exception:
            return False

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user profile by ID
        """
        query = "SELECT * FROM user_profiles WHERE id = ?"
        results = self.execute_query(query, (user_id,))
        if results:
            return dict(results[0])
        return None

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a user profile by username
        """
        query = "SELECT * FROM user_profiles WHERE username = ?"
        results = self.execute_query(query, (username,))
        if results:
            return dict(results[0])
        return None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user profile by email
        """
        query = "SELECT * FROM user_profiles WHERE email = ?"
        results = self.execute_query(query, (email,))
        if results:
            return dict(results[0])
        return None

    def update(self, user_id: int, **kwargs) -> bool:
        """
        Update a user profile with provided fields
        """
        allowed_fields = {'username', 'email', 'first_name', 'last_name', 'currency', 'timezone'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not update_fields:
            return False

        # Validate fields before updating
        for field, value in update_fields.items():
            if field == 'email':
                is_valid, msg = self.validate_email(value)
                if not is_valid:
                    raise ValueError(f"Invalid email: {msg}")
            elif field == 'username':
                is_valid, msg = self.validate_username(value)
                if not is_valid:
                    raise ValueError(f"Invalid username: {msg}")

        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [user_id]

        query = f"UPDATE user_profiles SET {set_clause} WHERE id = ?"
        try:
            self.execute_update(query, values)
            return True
        except Exception:
            return False

    def delete(self, user_id: int) -> bool:
        """
        Delete a user profile by ID
        """
        query = "DELETE FROM user_profiles WHERE id = ?"
        try:
            self.execute_update(query, (user_id,))
            return True
        except Exception:
            return False