#!/usr/bin/env python3
"""
Test script for enhanced expense categorizer to verify >90% accuracy
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ml_models.enhanced_expense_categorizer import EnhancedExpenseCategorizer

def test_enhanced_categorizer():
    """
    Test the enhanced categorizer to ensure it meets the 90% accuracy requirement
    """
    print("🧪 Testing Enhanced Expense Categorizer")
    print("=" * 50)

    # Create and train the enhanced categorizer
    categorizer = EnhancedExpenseCategorizer()

    print("🚀 Training the enhanced model...")
    accuracy = categorizer.train()

    print(f"✅ Training completed with accuracy: {accuracy:.1%}")

    # Test with comprehensive test cases
    test_cases = [
        # Food & Dining
        ("bought groceries at walmart including milk eggs and bread", "Food & Dining"),
        ("pizza delivery from dominos", "Food & Dining"),
        ("coffee at starbucks", "Food & Dining"),
        ("restaurant dinner with friends", "Food & Dining"),
        ("lunch at subway sandwich", "Food & Dining"),

        # Transportation
        ("gas for car at shell station", "Transportation"),
        ("uber ride to airport", "Transportation"),
        ("train ticket for commute", "Transportation"),
        ("car maintenance and oil change", "Transportation"),
        ("parking fee downtown", "Transportation"),

        # Housing
        ("monthly rent payment for apartment", "Housing"),
        ("electricity bill from power company", "Utilities"),
        ("water bill payment", "Utilities"),
        ("mortgage payment", "Housing"),
        ("home insurance premium", "Insurance"),

        # Entertainment
        ("movie tickets at cinema", "Entertainment"),
        ("netflix subscription", "Entertainment"),
        ("gym membership", "Entertainment"),
        ("concert tickets", "Entertainment"),
        ("video game purchase", "Entertainment"),

        # Healthcare
        ("doctor appointment and consultation", "Healthcare"),
        ("prescription medication at pharmacy", "Healthcare"),
        ("dental checkup", "Healthcare"),
        ("health insurance premium", "Insurance"),
        ("hospital visit", "Healthcare"),

        # Shopping
        ("clothing purchase at target", "Shopping"),
        ("electronics from best buy", "Shopping"),
        ("book purchase online", "Shopping"),
        ("jewelry gift", "Shopping"),
        ("home decor items", "Shopping"),

        # Travel
        ("flight ticket to california", "Travel"),
        ("hotel reservation in vegas", "Travel"),
        ("car rental for vacation", "Travel"),
        ("cruise booking", "Travel"),
        ("travel insurance", "Insurance"),

        # Education
        ("tuition payment for college", "Education"),
        ("textbooks for semester", "Education"),
        ("online course enrollment", "Education"),
        ("school supplies", "Education"),
        ("student loan payment", "Debt Payment"),

        # Income
        ("monthly salary deposit", "Salary"),
        ("freelance payment received", "Salary"),
        ("investment dividends", "Investment"),
        ("bonus payment", "Salary"),
        ("side job earnings", "Salary"),

        # Utilities
        ("gas and electric bill", "Utilities"),
        ("internet service provider", "Utilities"),
        ("cable tv subscription", "Utilities"),
        ("phone bill", "Utilities"),
        ("water and sewer", "Utilities"),

        # Personal Care
        ("hair salon appointment", "Personal Care"),
        ("cosmetics purchase", "Personal Care"),
        ("skincare products", "Personal Care"),
        ("nail salon manicure", "Personal Care"),
        ("shaving supplies", "Personal Care"),

        # Insurance
        ("auto insurance premium", "Insurance"),
        ("life insurance payment", "Insurance"),
        ("disability insurance", "Insurance"),
        ("homeowners insurance", "Insurance"),
        ("health insurance", "Insurance"),

        # Debt Payment
        ("credit card payment", "Debt Payment"),
        ("student loan payment", "Debt Payment"),
        ("car loan payment", "Debt Payment"),
        ("mortgage payment", "Housing"),
        ("medical bill payment", "Debt Payment"),

        # Gifts & Donations
        ("birthday gift for friend", "Gifts & Donations"),
        ("charitable donation", "Gifts & Donations"),
        ("wedding gift", "Gifts & Donations"),
        ("donation to charity", "Gifts & Donations"),
        ("flowers for mother", "Gifts & Donations"),
    ]

    print(f"\n📝 Testing {len(test_cases)} comprehensive cases...")

    correct_predictions = 0
    total_tests = len(test_cases)

    for i, (description, expected_category) in enumerate(test_cases, 1):
        predicted_category, confidence = categorizer.predict(description)

        # Check if prediction matches (with some flexibility for similar categories)
        is_correct = predicted_category.lower() == expected_category.lower()

        if is_correct:
            correct_predictions += 1
            status = "✅"
        else:
            status = "❌"

        print(f"{status} Test {i:2d}: '{description[:30]}...' -> Predicted: {predicted_category} (Expected: {expected_category}) [Conf: {confidence:.2f}]")

    overall_accuracy = correct_predictions / total_tests if total_tests > 0 else 0

    print(f"\n📊 Results Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Correct: {correct_predictions}")
    print(f"   Incorrect: {total_tests - correct_predictions}")
    print(f"   Overall Accuracy: {overall_accuracy:.1%}")

    if overall_accuracy >= 0.90:
        print(f"🎉 SUCCESS: Enhanced categorizer achieved {overall_accuracy:.1%} accuracy (>90%)!")
    else:
        print(f"⚠️  WARNING: Enhanced categorizer achieved {overall_accuracy:.1%} accuracy (<90%)")

    # Test cross-validation performance
    print(f"\n🔄 Cross-validation test:")
    cv_results = categorizer.evaluate_model_detailed()
    print(f"   Cross-validation accuracy: {cv_results['mean_cv_accuracy']:.1%} ± {cv_results['std_cv_accuracy']:.1%}")

    # Save the trained model
    print(f"\n💾 Saving enhanced model...")
    categorizer.save_model()
    print("   Model saved successfully!")

    return overall_accuracy >= 0.90

if __name__ == "__main__":
    success = test_enhanced_categorizer()

    if success:
        print(f"\n✨ All tests passed! Enhanced categorizer is ready with >90% accuracy.")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed. Accuracy requirement not met.")
        sys.exit(1)