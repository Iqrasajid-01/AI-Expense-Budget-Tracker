"""
PostgreSQL Database Setup for Neon
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

def get_db_connection():
    """Get PostgreSQL database connection"""
    # Use environment variable if available (Vercel)
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        # Fallback to provided Neon connection string
        database_url = 'postgresql://neondb_owner:npg_4FBhJngN8SUL@ep-rapid-butterfly-addi5ohb-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
    
    try:
        conn = psycopg2.connect(database_url, sslmode='require')
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        print(f"Database URL: {database_url[:50]}...")
        raise

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
            INSERT INTO categories (name, type, icon)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        ''', (cat_name, cat_type, icon))

    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
    cursor.close()
    conn.close()

    print("PostgreSQL database initialized successfully!")
    return True

def create_user(username, email, password):
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        password_hash = generate_password_hash(password)

        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', (username, email, password_hash))

        user_id = cursor.fetchone()[0]

        # Create user profile
        cursor.execute('''
            INSERT INTO user_profiles (user_id)
            VALUES (%s)
        ''', (user_id,))

        conn.commit()
        return user_id
    except psycopg2.IntegrityError as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user"""
    from werkzeug.security import check_password_hash

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return dict(user)
    return None

def get_user_profile(user_id):
    """Get user profile data"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('SELECT * FROM user_profiles WHERE user_id = %s', (user_id,))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()

    if profile:
        return dict(profile)
    return None

def update_user_profile(user_id, email=None, currency=None, first_name=None, last_name=None):
    """Update user profile information"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update email in users table if provided
        if email:
            cursor.execute('''
                UPDATE users SET email = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (email, user_id))

        # Update profile in user_profiles table if provided
        if currency or first_name or last_name:
            # Check if profile exists
            cursor.execute('SELECT id FROM user_profiles WHERE user_id = %s', (user_id,))
            profile = cursor.fetchone()

            if profile:
                # Update existing profile
                updates = []
                values = []
                if currency:
                    updates.append('currency = %s')
                    values.append(currency)
                    updates.append('currency_symbol = %s')
                    values.append(get_currency_symbol(currency))
                if first_name:
                    updates.append('first_name = %s')
                    values.append(first_name)
                if last_name:
                    updates.append('last_name = %s')
                    values.append(last_name)

                if updates:
                    values.append(user_id)
                    query = f"UPDATE user_profiles SET {', '.join(updates)} WHERE user_id = %s"
                    cursor.execute(query, values)
            else:
                # Create new profile
                cursor.execute('''
                    INSERT INTO user_profiles (user_id, currency, currency_symbol, first_name, last_name)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (user_id, currency or 'USD', get_currency_symbol(currency or 'USD'), first_name or '', last_name or ''))

        conn.commit()
        return True
    except psycopg2.IntegrityError as e:
        print(f"Error updating profile: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_user_email(user_id, email):
    """Update user email"""
    if not email:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE users SET email = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (email, user_id))
        conn.commit()
        return True
    except psycopg2.IntegrityError as e:
        print(f"Error updating email: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def migrate_user_profiles():
    """Add new columns to user_profiles table for existing databases"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS first_name TEXT DEFAULT ''
        ''')
        print("Ensured first_name column exists")
    except Exception as e:
        print(f"first_name column check: {e}")

    try:
        cursor.execute('''
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS last_name TEXT DEFAULT ''
        ''')
        print("Ensured last_name column exists")
    except Exception as e:
        print(f"last_name column check: {e}")

    try:
        cursor.execute('''
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS currency_symbol TEXT DEFAULT '$'
        ''')
        print("Ensured currency_symbol column exists")
    except Exception as e:
        print(f"currency_symbol column check: {e}")

    conn.commit()
    cursor.close()
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

if __name__ == "__main__":
    print("Initializing PostgreSQL database...")
    init_db()
    print("\nDatabase setup complete!")
