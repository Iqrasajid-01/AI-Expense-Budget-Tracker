"""Retrain and verify the high-accuracy categorizer"""
from backend.ml_models.high_accuracy_categorizer import HighAccuracyCategorizer

cat = HighAccuracyCategorizer()
print('Training fresh model...')
acc = cat.train()
print(f'Accuracy: {acc:.1%}')

cat.save_model()
print('Model saved!\n')

# Test specific cases
tests = [
    'gas', 'gas station', 'netflix', 'shell', 'doctor', 'walmart',
    'starbucks', 'uber', 'amazon', 'cvs', 'marriott', 'tuition',
    'paycheck', 'electric bill', 'hair salon', 'geico', 'credit card',
    'birthday gift', 'flowers'
]
print('Predictions:')
for t in tests:
    c, conf = cat.predict(t)
    print(f'{t:20} -> {c:20} ({conf:.1%})')
