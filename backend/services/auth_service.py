"""
Authentication service with Flask-Login integration
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .db_service import DBService
from typing import Optional, Dict, Any


class User(UserMixin):
    """
    User class that extends Flask-Login's UserMixin
    """
    def __init__(self, user_data: Dict[str, Any]):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.currency = user_data.get('currency', 'USD')
        self.timezone = user_data.get('timezone', 'UTC')
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')


class AuthService:
    """
    Authentication service providing user authentication and management
    """
    def __init__(self):
        self.db_service = DBService()

    def register_user(self, username: str, email: str, password: str) -> Optional[User]:
        """
        Register a new user with the provided credentials
        """
        # Hash the password
        password_hash = generate_password_hash(password)

        # Create user in database
        user_data = self.db_service.create_user(username, email, password_hash)
        if user_data:
            return User(user_data)
        return None

    def register_user_with_validation(self, username: str, email: str, password: str,
                                    first_name: str = None, last_name: str = None) -> tuple[Optional[User], list]:
        """
        Register a new user with validation
        Returns (user, errors)
        """
        errors = []

        # Validate username
        from .utils import validate_email as validate_email_util, validate_password_strength, sanitize_text
        is_valid, msg = validate_email_util(email)
        if not is_valid:
            errors.append(f"Invalid email: {msg}")

        is_valid, msg = validate_password_strength(password)
        if not is_valid:
            errors.append(f"Invalid password: {msg}")

        # Basic username validation
        if not username or len(username.strip()) < 3:
            errors.append("Username must be at least 3 characters long")

        if errors:
            return None, errors

        # Sanitize inputs
        username = sanitize_text(username)
        email = sanitize_text(email)
        first_name = sanitize_text(first_name) if first_name else None
        last_name = sanitize_text(last_name) if last_name else None

        # Create user in database
        user_data = self.db_service.create_user(username, email, password, first_name, last_name)
        if user_data:
            return User(user_data), []
        else:
            errors.append("Username or email already exists")
            return None, errors

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with the provided credentials
        """
        # Get user from database
        user_data = self.db_service.get_user_by_username(username)
        if user_data and check_password_hash(user_data['password_hash'], password):
            return User(user_data)
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by their ID
        """
        user_data = self.db_service.get_user_by_id(user_id)
        if user_data:
            return User(user_data)
        return None

    def update_user_profile(self, user_id: int, **kwargs) -> bool:
        """
        Update user profile with provided fields
        """
        return self.db_service.update_user(user_id, **kwargs)

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user's password after verifying current password
        """
        user_data = self.db_service.get_user_by_id(user_id)
        if not user_data:
            return False

        # Verify current password
        if not check_password_hash(user_data['password_hash'], current_password):
            return False

        # Hash new password and update
        new_password_hash = generate_password_hash(new_password)
        return self.db_service.update_user(user_id, password_hash=new_password_hash)

    def update_user_profile(self, user_id: int, **kwargs) -> tuple[bool, list]:
        """
        Update user profile with validation
        Returns (success, errors)
        """
        errors = []

        # Validate email if provided
        if 'email' in kwargs and kwargs['email']:
            from .utils import validate_email as validate_email_util
            is_valid, msg = validate_email_util(kwargs['email'])
            if not is_valid:
                errors.append(f"Invalid email: {msg}")

        # Validate username if provided
        if 'username' in kwargs and kwargs['username']:
            if len(kwargs['username']) < 3:
                errors.append("Username must be at least 3 characters long")

        if errors:
            return False, errors

        # Sanitize inputs
        from .utils import sanitize_text
        for key in ['username', 'first_name', 'last_name']:
            if key in kwargs and kwargs[key]:
                kwargs[key] = sanitize_text(kwargs[key])

        success = self.db_service.update_user(user_id, **kwargs)
        return success, errors if not success else []