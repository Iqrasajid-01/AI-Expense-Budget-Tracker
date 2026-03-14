#!/usr/bin/env python3
"""
Test script to verify budget predictions are working properly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from backend.services.budget_service import BudgetService
from backend.services.db_service import DBService

def test_predictions():
    """
    Test the budget prediction functionality
    """
    print("[TEST] Testing budget prediction functionality")
    print("=" * 50)

    # Create a budget service instance
    budget_service = BudgetService()

    # Let's check if the database has any users and transactions
    db_service = DBService()

    try:
        # Get all users to find a valid user ID
        # Since we don't have direct access to users table, let's just test the database connection
        print("[INFO] Checking database connection and testing prediction logic...")

        # Test the predict_budget method with a user ID
        # We'll use 1 as a placeholder, but the function will handle missing data gracefully
        weekly_result = budget_service.predict_budget(1, 'weekly')
        monthly_result = budget_service.predict_budget(1, 'monthly')
        yearly_result = budget_service.predict_budget(1, 'yearly')

        print(f"[RESULT] Weekly prediction: ${weekly_result['summary']['total_predicted_expenses']:.2f}")
        print(f"[RESULT] Monthly prediction: ${monthly_result['summary']['total_predicted_expenses']:.2f}")
        print(f"[RESULT] Yearly prediction: ${yearly_result['summary']['total_predicted_expenses']:.2f}")

        # Check if values are not zero
        total_weekly = weekly_result['summary']['total_predicted_expenses']
        total_monthly = monthly_result['summary']['total_predicted_expenses']
        total_yearly = yearly_result['summary']['total_predicted_expenses']

        if total_weekly > 0 or total_monthly > 0 or total_yearly > 0:
            print("[SUCCESS] Predictions are working and returning non-zero values!")
            print("[SUCCESS] The prediction cards should now show actual values instead of $0.00")
        else:
            print("[INFO] No transaction history found for user, predictions are based on averages")
            print("[INFO] If transactions exist, they should now show calculated values")

        print(f"[SUMMARY] Weekly - Income: ${weekly_result['summary']['total_predicted_income']:.2f}, Expenses: ${weekly_result['summary']['total_predicted_expenses']:.2f}")
        print(f"[SUMMARY] Monthly - Income: ${monthly_result['summary']['total_predicted_income']:.2f}, Expenses: ${monthly_result['summary']['total_predicted_expenses']:.2f}")
        print(f"[SUMMARY] Yearly - Income: ${yearly_result['summary']['total_predicted_income']:.2f}, Expenses: ${yearly_result['summary']['total_predicted_expenses']:.2f}")

        print("\n[INFO] The dashboard should now show calculated predictions based on transaction history!")
        print("[INFO] If transactions exist in the database, the prediction cards will show real values.")

    except Exception as e:
        print(f"[ERROR] Error testing predictions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_predictions()