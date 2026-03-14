"""
Budget service for budget analytics and prediction functionality
"""
import pandas as pd
from .db_service import DBService
try:
    from ..ml_models.budget_predictor import BudgetPredictor
except ImportError:
    # Handle the case where the module is not available
    class BudgetPredictor:
        def __init__(self):
            self.model = None

        def load_model(self, model_path):
            pass

        def train_all_models(self, transactions, category=None):
            pass

        def save_model(self):
            pass
from typing import Dict, List, Any, Optional
import os


class BudgetService:
    """
    Budget service providing analytics and prediction functionality
    """
    def __init__(self):
        self.db_service = DBService()
        self.budget_predictor = BudgetPredictor()
        self.model_loaded = False

        # Try to load the trained model
        model_path = "ml_models/trained_models/budget_predictor.pkl"
        if os.path.exists(model_path):
            try:
                self.budget_predictor.load_model(model_path)
                self.model_loaded = True
            except Exception as e:
                print(f"Could not load existing budget prediction model: {e}")

    def train_prediction_models(self, user_id: int, category: str = None):
        """
        Train budget prediction models for a user
        """
        # Get user's transaction history
        transactions = self.db_service.get_user_transactions(user_id)

        if not transactions:
            print(f"No transactions found for user {user_id} to train budget prediction models")
            return

        # Train the prediction models
        self.budget_predictor.train_all_models(transactions, category)

        # Save the trained models
        self.budget_predictor.save_model()

        self.model_loaded = True

    def predict_budget(self, user_id: int, period_type: str = 'monthly',
                      start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Generate budget predictions for a user
        """
        if not self.model_loaded:
            # Try to train models with user data if not already loaded
            try:
                self.train_prediction_models(user_id)
            except Exception as e:
                print(f"Error training models: {e}")

        # Get user's transaction history to calculate predictions based on actual spending
        transactions = self.db_service.get_user_transactions(user_id)

        # Calculate predictions based on user's historical spending
        if not transactions:
            # If no transactions, return zero predictions
            return {
                'predictions': [],
                'summary': {
                    'total_predicted_income': 0,
                    'total_predicted_expenses': 0,
                    'predicted_savings': 0
                }
            }

        # Calculate average spending for different time periods
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])

        # Calculate weekly average spending
        weekly_avg = 0
        monthly_avg = 0
        yearly_avg = 0

        # Group expenses and calculate averages
        expense_transactions = df[df['type'] == 'expense']
        if not expense_transactions.empty:
            # Calculate weekly average
            expense_transactions['week'] = expense_transactions['date'].dt.to_period('W')
            weekly_spending = expense_transactions.groupby('week')['amount'].sum()
            if len(weekly_spending) > 0:
                weekly_avg = weekly_spending.mean()

            # Calculate monthly average
            expense_transactions['month'] = expense_transactions['date'].dt.to_period('M')
            monthly_spending = expense_transactions.groupby('month')['amount'].sum()
            if len(monthly_spending) > 0:
                monthly_avg = monthly_spending.mean()

            # Calculate yearly average
            expense_transactions['year'] = expense_transactions['date'].dt.year
            yearly_spending = expense_transactions.groupby('year')['amount'].sum()
            if len(yearly_spending) > 0:
                yearly_avg = yearly_spending.mean()

        # Calculate income averages too
        income_transactions = df[df['type'] == 'income']
        weekly_income_avg = 0
        monthly_income_avg = 0
        yearly_income_avg = 0

        if not income_transactions.empty:
            # Calculate weekly average income
            income_transactions['week'] = income_transactions['date'].dt.to_period('W')
            weekly_income = income_transactions.groupby('week')['amount'].sum()
            if len(weekly_income) > 0:
                weekly_income_avg = weekly_income.mean()

            # Calculate monthly average income
            income_transactions['month'] = income_transactions['date'].dt.to_period('M')
            monthly_income = income_transactions.groupby('month')['amount'].sum()
            if len(monthly_income) > 0:
                monthly_income_avg = monthly_income.mean()

            # Calculate yearly average income
            income_transactions['year'] = income_transactions['date'].dt.year
            yearly_income = income_transactions.groupby('year')['amount'].sum()
            if len(yearly_income) > 0:
                yearly_income_avg = yearly_income.mean()

        # Return predictions based on calculated averages
        if period_type == 'weekly':
            total_predicted_expenses = weekly_avg
            total_predicted_income = weekly_income_avg
        elif period_type == 'yearly':
            total_predicted_expenses = yearly_avg
            total_predicted_income = yearly_income_avg
        else:  # monthly (default)
            total_predicted_expenses = monthly_avg
            total_predicted_income = monthly_income_avg

        predicted_savings = total_predicted_income - total_predicted_expenses

        return {
            'predictions': [],  # We don't need individual predictions for dashboard
            'summary': {
                'total_predicted_income': total_predicted_income,
                'total_predicted_expenses': total_predicted_expenses,
                'predicted_savings': predicted_savings
            }
        }

    def get_budget_performance(self, user_id: int, budget_id: int) -> Dict[str, Any]:
        """
        Get performance metrics for a specific budget
        """
        # This would typically query the database for the budget and related transactions
        # For now, we'll simulate the functionality
        return {
            'budget_id': budget_id,
            'allocated_amount': 1000.0,
            'used_amount': 750.0,
            'remaining_amount': 250.0,
            'usage_percentage': 75.0
        }

    def get_category_budget_history(self, user_id: int, category_id: int) -> List[Dict[str, Any]]:
        """
        Get historical budget data for a category
        """
        # This would typically query the database for historical budgets
        # For now, we'll return sample data
        return [
            {
                'period_start': '2023-01-01',
                'period_end': '2023-01-31',
                'allocated_amount': 500.0,
                'actual_amount': 450.0,
                'variance': 50.0
            },
            {
                'period_start': '2023-02-01',
                'period_end': '2023-02-28',
                'allocated_amount': 500.0,
                'actual_amount': 520.0,
                'variance': -20.0
            }
        ]

    def create_budget_plan(self, user_id: int, category_id: int, amount: float,
                          period_start: str, period_end: str, budget_type: str = 'monthly') -> Optional[Dict[str, Any]]:
        """
        Create a new budget plan for the user
        """
        # Create the budget in the database
        budget = self.db_service.create_budget(user_id, category_id, amount, period_start, period_end, budget_type)
        return budget

    def get_user_budgets(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all budgets for a user
        """
        return self.db_service.get_user_budgets(user_id)

    def get_budget_advice(self, user_id: int) -> List[str]:
        """
        Get budget advice based on spending patterns
        """
        # Get user's transactions
        transactions = self.db_service.get_user_transactions(user_id)

        if not transactions:
            return ["No transaction data available to provide budget advice"]

        # Analyze spending patterns
        advice = []

        # Example: Check for overspending in certain categories
        category_totals = {}
        for transaction in transactions:
            category = transaction.get('category_name', 'Uncategorized')
            if category not in category_totals:
                category_totals[category] = 0
            if transaction.get('type') == 'expense':
                category_totals[category] += transaction['amount']

        # Identify top spending categories
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        if sorted_categories:
            top_category, top_amount = sorted_categories[0]
            advice.append(f"You spend the most on {top_category} (${top_amount:.2f}). Consider setting a budget for this category.")

        # Check for irregular spending
        if len(transactions) > 30:  # If we have at least 30 transactions
            recent_avg = sum(t['amount'] for t in transactions[-10]) / 10
            older_avg = sum(t['amount'] for t in transactions[-30:-20]) / 10
            if recent_avg > older_avg * 1.5:
                advice.append("Your recent spending has increased significantly. Review your expenses.")

        return advice

    def calculate_budget_variance(self, user_id: int, budget_id: int) -> Dict[str, float]:
        """
        Calculate variance between budgeted and actual amounts
        """
        # This would typically compare budget data with actual transaction data
        # For now, return sample data
        return {
            'budgeted_amount': 1000.0,
            'actual_amount': 950.0,
            'variance': 50.0,
            'variance_percentage': 5.0
        }

    def get_spending_trends(self, user_id: int, category: str = None) -> Dict[str, Any]:
        """
        Get spending trends for a user
        """
        # Get user's transactions
        transactions = self.db_service.get_user_transactions(user_id)

        if not transactions:
            return {'trends': [], 'average_monthly_spending': 0.0}

        # Calculate monthly spending
        monthly_spending = {}
        for transaction in transactions:
            if transaction.get('type') == 'expense':
                date = transaction['date']
                month = date[:7]  # Extract YYYY-MM
                if month not in monthly_spending:
                    monthly_spending[month] = 0
                monthly_spending[month] += transaction['amount']

        # Convert to list of tuples and sort by date
        trends = [(month, amount) for month, amount in monthly_spending.items()]
        trends.sort(key=lambda x: x[0])

        # Calculate average monthly spending
        if trends:
            avg_monthly = sum(amount for _, amount in trends) / len(trends)
        else:
            avg_monthly = 0.0

        return {
            'trends': trends,
            'average_monthly_spending': avg_monthly
        }


if __name__ == "__main__":
    # Example usage
    budget_service = BudgetService()

    # This would require a real user ID in practice
    print("Budget service initialized.")
    print("Available methods:", [method for method in dir(budget_service) if not method.startswith('_')])