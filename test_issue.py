"""Test problematic classifications"""
from backend.ml_models.high_accuracy_categorizer import HighAccuracyCategorizer

cat = HighAccuracyCategorizer()
cat.load_model('backend/ml_models/trained_models/high_accuracy_categorizer.pkl')

# Test the problematic cases
tests = [
    'washing clothes', 'go to gym', 'laundry', 'exercise', 'workout',
    'clothes washing machine', 'movie theater', 'buy shoes', 'haircut',
    'electric company', 'doctor appointment', 'bus ticket', 'rent',
    'netflix', 'spotify', 'amazon', 'uber', 'starbucks'
]
print('Testing classifications:')
for t in tests:
    c, conf = cat.predict(t)
    print(f'{t:30} -> {c:20} ({conf:.1%})')
