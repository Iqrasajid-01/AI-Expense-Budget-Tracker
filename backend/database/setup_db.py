"""
Database initialization and setup
Creates all necessary tables for the budget tracker application
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

def get_db_path():
    """Get the database path"""
    # Check if running on Vercel (serverless environment)
    if os.environ.get('VERCEL'):
        # Use /tmp directory on Vercel (writable)
        db_dir = '/tmp/budget_tracker'
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, 'budget_tracker.db')

    # Local development - use backend/database folder
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'budget_tracker.db')

def init_db():
    """Initialize the database with all required tables"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            initial_budget REAL DEFAULT 0.0,
            currency TEXT DEFAULT 'USD',
            first_name TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            currency_symbol TEXT DEFAULT '$',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT DEFAULT 'expense',
            icon TEXT DEFAULT 'fas fa-tag'
        )
    ''')
    
    # Insert default categories
    default_categories = [
        ('Food & Dining', 'expense', 'fas fa-utensils'),
        ('Transportation', 'expense', 'fas fa-car'),
        ('Housing', 'expense', 'fas fa-home'),
        ('Entertainment', 'expense', 'fas fa-film'),
        ('Healthcare', 'expense', 'fas fa-heartbeat'),
        ('Shopping', 'expense', 'fas fa-shopping-bag'),
        ('Travel', 'expense', 'fas fa-plane'),
        ('Education', 'expense', 'fas fa-graduation-cap'),
        ('Salary', 'income', 'fas fa-money-bill-wave'),
        ('Investment', 'income', 'fas fa-chart-line'),
        ('Utilities', 'expense', 'fas fa-lightbulb'),
        ('Personal Care', 'expense', 'fas fa-spa'),
        ('Insurance', 'expense', 'fas fa-shield-alt'),
        ('Debt Payment', 'expense', 'fas fa-credit-card'),
        ('Gifts & Donations', 'expense', 'fas fa-gift')
    ]
    
    for cat_name, cat_type, icon in default_categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, type, icon)
            VALUES (?, ?, ?)
        ''', (cat_name, cat_type, icon))
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            date DATE NOT NULL,
            description TEXT NOT NULL,
            category_id INTEGER,
            type TEXT DEFAULT 'expense',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
    ''')
    
    # Create budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            amount REAL NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            budget_type TEXT DEFAULT 'monthly',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_budgets_user ON budgets(user_id)')
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at: {db_path}")
    return db_path

def create_user(username, email, password):
    """Create a new user"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        user_id = cursor.lastrowid
        
        # Create user profile
        cursor.execute('''
            INSERT INTO user_profiles (user_id)
            VALUES (?)
        ''', (user_id,))
        
        conn.commit()
        return user_id
    except sqlite3.IntegrityError as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user"""
    from werkzeug.security import check_password_hash
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return dict(user)
    return None

def get_user_profile(user_id):
    """Get user profile data"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    conn.close()

    if profile:
        return dict(profile)
    return None

def update_user_profile(user_id, email=None, currency=None, first_name=None, last_name=None):
    """Update user profile information"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Update email in users table if provided
        if email:
            cursor.execute('''
                UPDATE users SET email = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (email, user_id))

        # Update profile in user_profiles table if provided
        if currency or first_name or last_name:
            # Check if profile exists
            cursor.execute('SELECT id FROM user_profiles WHERE user_id = ?', (user_id,))
            profile = cursor.fetchone()

            if profile:
                # Update existing profile
                updates = []
                values = []
                if currency:
                    updates.append('currency = ?')
                    values.append(currency)
                    updates.append('currency_symbol = ?')
                    values.append(get_currency_symbol(currency))
                if first_name:
                    updates.append('first_name = ?')
                    values.append(first_name)
                if last_name:
                    updates.append('last_name = ?')
                    values.append(last_name)

                if updates:
                    values.append(user_id)
                    query = f"UPDATE user_profiles SET {', '.join(updates)} WHERE user_id = ?"
                    cursor.execute(query, values)
            else:
                # Create new profile
                cursor.execute('''
                    INSERT INTO user_profiles (user_id, currency, currency_symbol, first_name, last_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, currency or 'USD', get_currency_symbol(currency or 'USD'), first_name or '', last_name or ''))

        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Error updating profile: {e}")
        return False
    finally:
        conn.close()

def update_user_email(user_id, email):
    """Update user email"""
    if not email:
        return False
        
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE users SET email = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (email, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Error updating email: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("\nDatabase setup complete!")
    print("\nYou can now run the application with: python backend/app.py")

def migrate_user_profiles():
    """Add new columns to user_profiles table for existing databases"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Try to add first_name column
        cursor.execute('''
            ALTER TABLE user_profiles ADD COLUMN first_name TEXT DEFAULT ''
        ''')
        print("Added first_name column to user_profiles")
    except sqlite3.OperationalError:
        print("first_name column already exists")

    try:
        # Try to add last_name column
        cursor.execute('''
            ALTER TABLE user_profiles ADD COLUMN last_name TEXT DEFAULT ''
        ''')
        print("Added last_name column to user_profiles")
    except sqlite3.OperationalError:
        print("last_name column already exists")

    try:
        # Try to add currency_symbol column
        cursor.execute('''
            ALTER TABLE user_profiles ADD COLUMN currency_symbol TEXT DEFAULT '$'
        ''')
        print("Added currency_symbol column to user_profiles")
    except sqlite3.OperationalError:
        print("currency_symbol column already exists")

    conn.commit()
    conn.close()
    print("Migration complete!")

def get_currency_symbol(currency_code):
    """Get currency symbol from currency code"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥'
    }
    return symbols.get(currency_code, '$')
