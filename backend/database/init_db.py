import sqlite3
import os
from datetime import datetime

def init_db():
    """Initialize the SQLite database with the schema"""
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)

    # Connect to database
    conn = sqlite3.connect('database/budget_app.db')
    cursor = conn.cursor()

    # Read schema from SQL file
    with open('database/schema.sql', 'r') as schema_file:
        schema_sql = schema_file.read()

    # Execute schema
    cursor.executescript(schema_sql)

    # Commit and close
    conn.commit()
    conn.close()

    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()