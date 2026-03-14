-- Database schema for Personalized Budget Planning and Expense Categorization System

-- UserProfile table
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    currency TEXT DEFAULT 'USD',
    timezone TEXT DEFAULT 'UTC',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Category table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    color_code TEXT DEFAULT '#000000',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Transaction table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    date DATE NOT NULL,
    description TEXT NOT NULL,
    category_id INTEGER,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles (id),
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

-- Budget table
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER,
    amount REAL NOT NULL CHECK (amount >= 0),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    budget_type TEXT DEFAULT 'monthly' CHECK (budget_type IN ('weekly', 'monthly', 'yearly')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles (id),
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

-- ML Model table
CREATE TABLE IF NOT EXISTS ml_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_type TEXT NOT NULL CHECK (model_type IN ('categorization', 'prediction')),
    model_path TEXT NOT NULL,
    training_date DATETIME NOT NULL,
    accuracy_score REAL,  -- For categorization models
    performance_metrics TEXT,  -- JSON serialized performance metrics
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (model_type) REFERENCES categories (id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions (user_id, date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions (category_id);
CREATE INDEX IF NOT EXISTS idx_budget_user_category_period ON budgets (user_id, category_id, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_transactions_type_date ON transactions (type, date);

-- Trigger to update the updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_user_profiles_timestamp
AFTER UPDATE ON user_profiles
FOR EACH ROW
BEGIN
    UPDATE user_profiles SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_transactions_timestamp
AFTER UPDATE ON transactions
FOR EACH ROW
BEGIN
    UPDATE transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_budgets_timestamp
AFTER UPDATE ON budgets
FOR EACH ROW
BEGIN
    UPDATE budgets SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Insert default categories
INSERT OR IGNORE INTO categories (name, description, color_code) VALUES
('Food', 'Groceries and dining expenses', '#FF6B6B'),
('Transportation', 'Gas, public transport, vehicle expenses', '#4ECDC4'),
('Housing', 'Rent, mortgage, utilities', '#45B7D1'),
('Entertainment', 'Movies, hobbies, recreation', '#96CEB4'),
('Healthcare', 'Medical expenses and insurance', '#FFEAA7'),
('Shopping', 'Retail purchases', '#DDA0DD'),
('Travel', 'Vacation and business travel', '#98D8C8'),
('Education', 'Tuition and learning materials', '#F7DC6F'),
('Salary', 'Income from employment', '#BB8FCE'),
('Investment', 'Investment income', '#85C1E9');