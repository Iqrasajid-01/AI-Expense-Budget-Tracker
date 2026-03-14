"""
Error handling and logging mechanisms
"""
import logging
from functools import wraps
from flask import jsonify, request
from typing import Callable, Any


def setup_logging():
    """
    Set up logging configuration for the application
    """
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()  # Also log to console
        ]
    )


def log_function_call(func: Callable) -> Callable:
    """
    Decorator to log function calls
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling function: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logging.info(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logging.error(f"Error in function {func.__name__}: {str(e)}")
            raise
    return wrapper


def handle_error(error_msg: str, status_code: int = 500):
    """
    Standardized error response
    """
    logging.error(error_msg)
    return jsonify({
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': error_msg
        }
    }), status_code


def validate_input(data: dict, required_fields: list) -> tuple:
    """
    Validate required fields in input data
    Returns (is_valid: bool, error_message: str)
    """
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            return False, f"Missing required field: {field}"
    return True, ""


class ErrorHandler:
    """
    Centralized error handling class
    """
    @staticmethod
    def handle_validation_error(field_name: str) -> tuple:
        error_msg = f"Validation error: Invalid value for {field_name}"
        logging.warning(error_msg)
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error_msg
            }
        }), 400

    @staticmethod
    def handle_not_found(resource_type: str, resource_id: str = None) -> tuple:
        if resource_id:
            error_msg = f"{resource_type} with ID {resource_id} not found"
        else:
            error_msg = f"{resource_type} not found"
        logging.warning(error_msg)
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': error_msg
            }
        }), 404

    @staticmethod
    def handle_forbidden() -> tuple:
        error_msg = "Access forbidden"
        logging.warning(error_msg)
        return jsonify({
            'error': {
                'code': 'FORBIDDEN',
                'message': error_msg
            }
        }), 403

    @staticmethod
    def handle_internal_error(error: Exception) -> tuple:
        error_msg = f"Internal server error: {str(error)}"
        logging.error(error_msg, exc_info=True)
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': "An internal server error occurred"
            }
        }), 500