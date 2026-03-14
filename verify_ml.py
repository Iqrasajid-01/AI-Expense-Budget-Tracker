"""Quick verification that ML service works"""
from backend.services.ml_service import MLService

ml = MLService()
print('ML Service initialized successfully!')
print(f'Model loaded: {ml.model_loaded}')
print(f'Categories: {len(ml.get_available_categories())} categories available')

# Quick prediction test
test_inputs = ['walmart groceries', 'gas station', 'netflix', 'doctor']
print('\nQuick tests:')
for text in test_inputs:
    cat, conf = ml.categorize_transaction(text)
    print(f'  "{text}" -> {cat} ({conf:.1%})')
