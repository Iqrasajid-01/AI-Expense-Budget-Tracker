"""
Integration tests for the budget planning system
"""
import unittest
import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.db_service import DBService
from backend.services.auth_service import AuthService
from backend.models.transaction import Transaction
from backend.models.user_profile import UserProfile
from backend.ml_models.expense_categorizer import ExpenseCategorizer


class TestIntegration(unittest.TestCase):
    """
    Integration tests for the budget planning system
    """

    def setUp(self):
        """
        Set up test fixtures before each test
        """
        self.db_service = DBService()
        self.auth_service = AuthService()
        self.transaction_model = Transaction()
        self.user_model = UserProfile()
        self.categorizer = ExpenseCategorizer()

        # Train categorizer for testing
        self.categorizer.train()

    def test_user_registration_and_authentication_flow(self):
        """
        Test the complete user registration and authentication flow
        """
        # Register a new user
        username = "test_user"
        email = "test@example.com"
        password = "SecurePassword123!"

        user = self.auth_service.register_user(username, email, password)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)

        # Authenticate the user
        authenticated_user = self.auth_service.authenticate_user(username, password)
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.username, username)

        # Attempt to authenticate with wrong password
        failed_auth = self.auth_service.authenticate_user(username, "wrong_password")
        self.assertIsNone(failed_auth)

    def test_transaction_crud_operations(self):
        """
        Test the complete transaction CRUD flow
        """
        # Create a test user
        username = "test_transaction_user"
        email = "trans_test@example.com"
        password = "SecurePassword123!"

        user = self.auth_service.register_user(username, email, password)
        self.assertIsNotNone(user)

        # Create a transaction
        transaction_data = {
            'user_id': user.id,
            'amount': 50.0,
            'date': '2023-01-01',
            'description': 'grocery shopping',
            'type': 'expense'
        }

        created_transaction = self.db_service.create_transaction(
            user_id=user.id,
            amount=50.0,
            date='2023-01-01',
            description='grocery shopping',
            type='expense'
        )

        self.assertIsNotNone(created_transaction)
        self.assertEqual(created_transaction['amount'], 50.0)
        self.assertEqual(created_transaction['description'], 'grocery shopping')

        # Retrieve the transaction
        retrieved_transaction = self.db_service.get_transaction_by_id(created_transaction['id'])
        self.assertIsNotNone(retrieved_transaction)
        self.assertEqual(retrieved_transaction['id'], created_transaction['id'])

        # Update the transaction
        update_success = self.db_service.update_transaction(
            created_transaction['id'],
            amount=75.0,
            description='updated grocery shopping'
        )
        self.assertTrue(update_success)

        # Verify the update
        updated_transaction = self.db_service.get_transaction_by_id(created_transaction['id'])
        self.assertIsNotNone(updated_transaction)
        self.assertEqual(updated_transaction['amount'], 75.0)
        self.assertEqual(updated_transaction['description'], 'updated grocery shopping')

        # Delete the transaction
        delete_success = self.db_service.delete_transaction(created_transaction['id'])
        self.assertTrue(delete_success)

        # Verify deletion
        deleted_transaction = self.db_service.get_transaction_by_id(created_transaction['id'])
        self.assertIsNone(deleted_transaction)

    def test_ml_categorization_integration(self):
        """
        Test ML categorization integration with transaction creation
        """
        # Create a test user
        username = "test_ml_user"
        email = "ml_test@example.com"
        password = "SecurePassword123!"

        user = self.auth_service.register_user(username, email, password)
        self.assertIsNotNone(user)

        # Create a transaction without specifying category
        description = "grocery shopping at walmart"

        # Use ML to categorize
        predicted_category, confidence = self.categorizer.predict(description)

        self.assertIsInstance(predicted_category, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

        # Create transaction with ML-predicted category
        transaction = self.db_service.create_transaction(
            user_id=user.id,
            amount=100.0,
            date='2023-01-01',
            description=description,
            category=predicted_category,  # Use ML prediction
            type='expense'
        )

        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['category_name'], predicted_category)

    def test_financial_summary_generation(self):
        """
        Test financial summary generation with multiple transactions
        """
        # Create a test user
        username = "test_summary_user"
        email = "summary_test@example.com"
        password = "SecurePassword123!"

        user = self.auth_service.register_user(username, email, password)
        self.assertIsNotNone(user)

        # Create multiple transactions
        transactions_data = [
            {'amount': 100.0, 'date': '2023-01-01', 'description': 'income', 'type': 'income'},
            {'amount': 50.0, 'date': '2023-01-02', 'description': 'expense1', 'type': 'expense'},
            {'amount': 30.0, 'date': '2023-01-03', 'description': 'expense2', 'type': 'expense'},
        ]

        for trans_data in transactions_data:
            transaction = self.db_service.create_transaction(
                user_id=user.id,
                amount=trans_data['amount'],
                date=trans_data['date'],
                description=trans_data['description'],
                type=trans_data['type']
            )
            self.assertIsNotNone(transaction)

        # Get financial summary
        summary = self.db_service.get_financial_summary(user.id)

        self.assertIsInstance(summary, dict)
        self.assertIn('summary', summary)
        self.assertIn('by_category', summary)
        self.assertIn('trends', summary)

        summary_data = summary['summary']
        self.assertIn('total_income', summary_data)
        self.assertIn('total_expenses', summary_data)
        self.assertIn('net_change', summary_data)
        self.assertIn('savings_rate', summary_data)

        # Verify calculations
        expected_income = sum(t['amount'] for t in transactions_data if t['type'] == 'income')
        expected_expenses = sum(t['amount'] for t in transactions_data if t['type'] == 'expense')
        expected_net = expected_income - expected_expenses

        self.assertEqual(summary_data['total_income'], expected_income)
        self.assertEqual(summary_data['total_expenses'], expected_expenses)
        self.assertEqual(summary_data['net_change'], expected_net)

    def test_user_profile_management(self):
        """
        Test user profile management integration
        """
        # Create a user
        username = "profile_test_user"
        email = "profile_test@example.com"
        password = "SecurePassword123!"

        user = self.auth_service.register_user(username, email, password)
        self.assertIsNotNone(user)

        # Update user profile
        update_success = self.auth_service.update_user_profile(
            user_id=user.id,
            first_name="John",
            last_name="Doe",
            currency="EUR"
        )
        self.assertTrue(update_success)

        # Retrieve updated user
        updated_user = self.auth_service.get_user_by_id(user.id)
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.first_name, "John")
        self.assertEqual(updated_user.last_name, "Doe")
        self.assertEqual(updated_user.currency, "EUR")

    def test_get_user_transactions(self):
        """
        Test retrieving user transactions
        """
        # Create a test user
        username = "test_trans_list_user"
        email = "trans_list_test@example.com"
        password = "SecurePassword123!"

        user = self.auth_service.register_user(username, email, password)
        self.assertIsNotNone(user)

        # Create multiple transactions
        for i in range(3):
            transaction = self.db_service.create_transaction(
                user_id=user.id,
                amount=50.0 + i * 10,
                date=f'2023-01-0{i+1}',
                description=f'Test transaction {i+1}',
                type='expense'
            )
            self.assertIsNotNone(transaction)

        # Get user transactions
        user_transactions = self.db_service.get_user_transactions(user.id)
        self.assertIsInstance(user_transactions, list)
        self.assertEqual(len(user_transactions), 3)

        # Verify transaction details
        for i, transaction in enumerate(user_transactions):
            self.assertEqual(transaction['amount'], 50.0 + i * 10)
            self.assertEqual(transaction['description'], f'Test transaction {i+1}')

    def tearDown(self):
        """
        Clean up after each test
        """
        # In a real test environment, you might want to clean up created data
        # For this test suite, we'll leave the data as is since we're using test-specific names
        pass


if __name__ == '__main__':
    unittest.main()