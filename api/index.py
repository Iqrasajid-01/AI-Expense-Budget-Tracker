"""
Vercel Serverless Entry Point
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from database.setup_postgres import init_db, migrate_user_profiles

# Initialize database before creating app (critical for Vercel serverless)
init_db()
migrate_user_profiles()

# Initialize ML service to train/load model on cold start
try:
    from services.ml_service import MLService
    print("Vercel: Initializing ML service...")
    ml_instance = MLService()
    print(f"Vercel: ML service initialized - model_loaded={ml_instance.model_loaded}, is_trained={ml_instance.expense_categorizer.is_trained if ml_instance else False}")
except Exception as e:
    print(f"Vercel: Warning - ML service initialization failed: {e}")
    print("Vercel: ML categorization will train on first request")

# Create the Flask app instance
app = create_app()

# For Vercel serverless deployment
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
