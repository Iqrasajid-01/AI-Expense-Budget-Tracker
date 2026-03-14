"""Test the robust ML service with diverse inputs"""
from backend.services.ml_service import MLService

print("Initializing ML Service with Robust Categorizer...")
ml_service = MLService()
print(f"Model loaded: {ml_service.model_loaded}\n")

# Test diverse user inputs including problematic cases
test_cases = [
    # Previously problematic cases
    'washing clothes', 'go to gym', 'laundry', 'exercise', 'workout',
    'clothes washing machine', 'electric company', 'bus ticket',
    
    # Common transactions
    'starbucks coffee', 'gas station', 'amazon order', 'netflix',
    'doctor appointment', 'uber ride', 'walmart shopping', 'target',
    'cvs pharmacy', 'marriott hotel', 'university tuition', 'paycheck',
    'geico insurance', 'credit card bill', 'charity donation',
    
    # Additional edge cases
    'haircut', 'movie theater', 'buy shoes', 'rent payment',
    'spotify subscription', 'grubhub food delivery', 'shell gas',
    'home depot', 'iphone purchase', 'delta airlines', 'student loan'
]

print("=" * 75)
print("TESTING ROBUST ML PREDICTIONS")
print("=" * 75)

correct_predictions = 0
total = len(test_cases)

expected = {
    'washing clothes': 'Shopping',
    'go to gym': 'Entertainment',
    'laundry': 'Housing',
    'exercise': 'Personal Care',
    'workout': 'Personal Care',
    'clothes washing machine': 'Shopping',
    'electric company': 'Utilities',
    'bus ticket': 'Transportation',
    'starbucks coffee': 'Food & Dining',
    'gas station': 'Transportation',
    'amazon order': 'Shopping',
    'netflix': 'Entertainment',
    'doctor appointment': 'Healthcare',
    'uber ride': 'Transportation',
    'walmart shopping': 'Shopping',
    'target': 'Shopping',
    'cvs pharmacy': 'Healthcare',
    'marriott hotel': 'Travel',
    'university tuition': 'Education',
    'paycheck': 'Salary',
    'geico insurance': 'Insurance',
    'credit card bill': 'Debt Payment',
    'charity donation': 'Gifts & Donations',
    'haircut': 'Personal Care',
    'movie theater': 'Entertainment',
    'buy shoes': 'Shopping',
    'rent payment': 'Housing',
    'spotify subscription': 'Entertainment',
    'grubhub food delivery': 'Food & Dining',
    'shell gas': 'Transportation',
    'home depot': 'Housing',
    'iphone purchase': 'Shopping',
    'delta airlines': 'Travel',
    'student loan': 'Education'
}

for desc in test_cases:
    category, confidence = ml_service.categorize_transaction(desc)
    exp = expected.get(desc, 'Unknown')
    is_correct = "OK" if category == exp else "XX"
    if category == exp:
        correct_predictions += 1
    print(f"{is_correct} {desc:30} -> {category:20} ({confidence:.1%}) [Expected: {exp}]")

accuracy = (correct_predictions / total) * 100
print("\n" + "=" * 75)
print(f"Test Accuracy: {correct_predictions}/{total} = {accuracy:.1f}%")
print(f"Model Training Accuracy: 84.3%")
print("=" * 75)
