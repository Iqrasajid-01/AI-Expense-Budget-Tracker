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

# Create the Flask app instance
app = create_app()

# For Vercel serverless deployment
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
