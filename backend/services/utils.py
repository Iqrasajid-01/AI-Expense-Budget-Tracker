"""
Utility functions for data validation and sanitization
"""
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
import html


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format
    Returns (is_valid, error_message)
    """
    if not email:
        return False, "Email cannot be empty"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(pattern, email) is not None

    if not is_valid:
        return False, "Invalid email format"

    return True, ""


def validate_amount(amount: Any) -> tuple[bool, str]:
    """
    Validate transaction amount
    Returns (is_valid, error_message)
    """
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            return False, "Amount must be greater than 0"
        if amount_float > 999999999:  # Max 999,999,999
            return False, "Amount is too large"
        return True, ""
    except (ValueError, TypeError):
        return False, "Amount must be a valid number"


def validate_date(date_str: str) -> tuple[bool, str]:
    """
    Validate date format (YYYY-MM-DD)
    Returns (is_valid, error_message)
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format"


def validate_transaction_type(trans_type: str) -> tuple[bool, str]:
    """
    Validate transaction type (income or expense)
    Returns (is_valid, error_message)
    """
    if trans_type.lower() not in ['income', 'expense']:
        return False, "Transaction type must be 'income' or 'expense'"
    return True, ""


def sanitize_text(text: str) -> str:
    """
    Sanitize text input to prevent XSS
    """
    if not isinstance(text, str):
        return ""
    # Remove HTML tags and escape special characters
    sanitized = html.escape(text)
    return sanitized.strip()


def validate_category_name(name: str) -> tuple[bool, str]:
    """
    Validate category name
    Returns (is_valid, error_message)
    """
    if not name or len(name.strip()) == 0:
        return False, "Category name cannot be empty"
    if len(name) > 50:
        return False, "Category name cannot exceed 50 characters"
    # Check for valid characters (letters, numbers, spaces, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        return False, "Category name contains invalid characters"
    return True, ""


def validate_color_code(color_code: str) -> tuple[bool, str]:
    """
    Validate hex color code
    Returns (is_valid, error_message)
    """
    if not color_code:
        return True, ""  # Color code is optional
    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color_code):
        return False, "Color code must be a valid hex color (e.g., #FF0000)"
    return True, ""


def validate_budget_period(start_date: str, end_date: str) -> tuple[bool, str]:
    """
    Validate budget period dates
    Returns (is_valid, error_message)
    """
    is_start_valid, start_msg = validate_date(start_date)
    if not is_start_valid:
        return False, f"Start date: {start_msg}"

    is_end_valid, end_msg = validate_date(end_date)
    if not is_end_valid:
        return False, f"End date: {end_msg}"

    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')

        if end_dt < start_dt:
            return False, "End date must be after start date"

        return True, ""
    except ValueError:
        return False, "Invalid date comparison"


def validate_budget_amount(amount: Any) -> tuple[bool, str]:
    """
    Validate budget amount
    Returns (is_valid, error_message)
    """
    try:
        amount_float = float(amount)
        if amount_float < 0:
            return False, "Budget amount cannot be negative"
        if amount_float > 999999999:  # Max 999,999,999
            return False, "Budget amount is too large"
        return True, ""
    except (ValueError, TypeError):
        return False, "Budget amount must be a valid number"


def sanitize_description(description: str) -> str:
    """
    Sanitize transaction description
    """
    if not isinstance(description, str):
        return ""

    # Limit length to prevent overly long descriptions
    if len(description) > 500:
        description = description[:500]

    # Sanitize HTML
    sanitized = html.escape(description)
    return sanitized.strip()


def validate_budget_type(budget_type: str) -> tuple[bool, str]:
    """
    Validate budget type (weekly, monthly, yearly)
    Returns (is_valid, error_message)
    """
    valid_types = ['weekly', 'monthly', 'yearly']
    if budget_type.lower() not in valid_types:
        return False, f"Budget type must be one of: {', '.join(valid_types)}"
    return True, ""


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    return True, ""


def clean_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and validate user input data
    """
    cleaned_data = {}

    for key, value in data.items():
        if value is None:
            cleaned_data[key] = None
            continue

        if key == 'email':
            cleaned_data[key] = sanitize_text(str(value))
        elif key == 'description':
            cleaned_data[key] = sanitize_description(str(value))
        elif key == 'name' or key == 'category' or key == 'username':
            cleaned_data[key] = sanitize_text(str(value))
        elif key in ['amount', 'budget_amount']:
            # Don't sanitize numbers, just validate
            cleaned_data[key] = value
        elif key in ['date', 'start_date', 'end_date']:
            # Don't sanitize dates, just validate
            cleaned_data[key] = value
        elif key == 'type':
            cleaned_data[key] = str(value).lower()
        elif key == 'color_code':
            cleaned_data[key] = str(value).lower()
        else:
            cleaned_data[key] = sanitize_text(str(value))

    return cleaned_data


def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format amount as currency
    """
    return f"{currency} {amount:,.2f}"


def extract_amount_from_text(text: str) -> Optional[float]:
    """
    Extract amount from text (useful for processing transaction descriptions that might contain amounts)
    """
    # Look for patterns like $123.45, 123.45, $123 etc.
    pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)'
    matches = re.findall(pattern, text)

    if matches:
        try:
            # Return the first amount found
            amount_str = matches[0].replace(',', '')
            return float(amount_str)
        except ValueError:
            return None

    return None