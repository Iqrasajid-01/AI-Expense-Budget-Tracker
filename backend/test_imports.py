import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("Testing imports...")
print(f"Backend dir: {backend_dir}")
print(f"Python path: {sys.path[:3]}...")
print()

try:
    from services.db_service_optimized import DBService
    print("✓ db_service_optimized.py imports OK")
    
    db = DBService()
    print("✓ DBService instantiation OK")
    
except Exception as e:
    print(f"✗ db_service_optimized.py error: {e}")
    import traceback
    traceback.print_exc()

print()

try:
    from services.ml_service_optimized import get_ml_service
    print("✓ ml_service_optimized.py imports OK")
    
    ml = get_ml_service()
    print("✓ get_ml_service() OK")
    
except Exception as e:
    print(f"✗ ml_service_optimized.py error: {e}")
    import traceback
    traceback.print_exc()

print()
print("All imports tested!")
