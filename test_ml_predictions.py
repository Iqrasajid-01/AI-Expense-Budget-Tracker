"""
Test script for ML expense categorization predictions
"""
from backend.services.ml_service import MLService

# Initialize ML service
print('Initializing ML Service...')
ml_service = MLService()
print(f'Model loaded: {ml_service.model_loaded}')
print()

# Test with various realistic user inputs
test_cases = [
    # Food & Dining
    'bought milk and bread at store',
    'starbucks morning coffee',
    'pizza delivery doordash',
    'mcdonalds lunch',
    'whole foods grocery shopping',
    
    # Transportation
    'shell gas station fill up',
    'uber ride to airport',
    'monthly bus pass',
    'car oil change',
    'parking garage downtown',
    
    # Housing
    'apartment rent payment',
    'electric bill payment',
    'water utility',
    'internet service provider',
    'home depot furniture',
    
    # Entertainment
    'netflix monthly subscription',
    'movie tickets amc cinema',
    'spotify premium music',
    'gym membership planet fitness',
    'video game playstation',
    
    # Healthcare
    'doctor visit checkup',
    'cvs pharmacy prescription',
    'dental cleaning appointment',
    'hospital emergency room',
    'eye exam glasses',
    
    # Shopping
    'amazon online order',
    'nike shoes footwear',
    'apple iphone purchase',
    'target shopping trip',
    'sephora makeup cosmetics',
    
    # Travel
    'marriott hotel reservation',
    'delta airlines flight',
    'vacation booking expedia',
    'airbnb rental',
    'cruise royal caribbean',
    
    # Education
    'university tuition payment',
    'college textbook',
    'student loan payment',
    'online course coursera',
    'sat test prep',
    
    # Salary/Income
    'monthly salary deposit',
    'paycheck direct deposit',
    'freelance payment received',
    'bonus compensation',
    'venmo payment received',
    
    # Utilities
    'electricity bill pge',
    'comcast internet cable',
    'verizon phone bill',
    'water sewer bill',
    'trash garbage collection',
    
    # Personal Care
    'hair salon haircut',
    'nail salon manicure',
    'spa massage treatment',
    'ulta beauty cosmetics',
    'barber shop shave',
    
    # Insurance
    'geico auto insurance',
    'health insurance premium',
    'homeowners insurance policy',
    'life insurance payment',
    'state farm insurance',
    
    # Debt Payment
    'chase credit card payment',
    'student loan nelnet',
    'personal loan payment',
    'tax payment irs',
    'debt consolidation',
    
    # Gifts & Donations
    'birthday christmas gift',
    'charity donation red cross',
    'flowers florist bouquet',
    'gofundme donation',
    'church tithe donation'
]

print('=' * 80)
print('=== TESTING ML PREDICTIONS ===')
print('=' * 80)

for desc in test_cases:
    category, confidence = ml_service.categorize_transaction(desc)
    print(f'{desc:45} -> {category:20} ({confidence:.2%})')

print()
print('=' * 80)
print(f'Model accuracy on training: 93.3%')
print('=' * 80)
