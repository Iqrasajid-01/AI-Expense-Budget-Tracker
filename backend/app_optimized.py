"""
Optimized Budget Tracker Application
Fast performance with connection pooling, caching, and lazy loading
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import optimized services
from database.setup_postgres import init_db, create_user, authenticate_user, get_user_by_id, migrate_user_profiles
from services.db_service_optimized import DBService
from services.ml_service_optimized import get_ml_service

# Enable Flask caching
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize services (fast - uses pooling/caching)
db_service = DBService()
ml_service = get_ml_service()

# Initialize database
init_db()
migrate_user_profiles()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(int(user_id))
    if user_data:
        user = UserMixin()
        user.id = user_data['id']
        user.username = user_data['username']
        return user
    return None

# Routes

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user_data = authenticate_user(username, password)
        if user_data:
            user = UserMixin()
            user.id = user_data['id']
            user.username = user_data['username']
            login_user(user)
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login_modern.html', error='Invalid username or password')

    return render_template('login_modern.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            return render_template('register_modern.html', error='All fields are required')

        if len(password) < 6:
            return render_template('register_modern.html', error='Password must be at least 6 characters')

        user_id = create_user(username, email, password)
        if user_id:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            return render_template('register_modern.html', error='Username or email already exists')

    return render_template('register_modern.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Optimized dashboard - uses aggregated queries"""
    user_id = session['user_id']

    # Get summary with single fast query (instead of loading all transactions)
    summary = db_service.get_user_transactions_summary(user_id)
    total_income = summary['total_income'] or 0
    total_expenses = summary['total_expenses'] or 0
    balance = summary['balance'] or 0

    # Get currency
    from database.setup_postgres import get_user_profile
    user_profile = get_user_profile(user_id)
    currency_symbol = user_profile.get('currency_symbol', '$') if user_profile else '$'

    # Get category breakdown (single optimized query)
    category_list = db_service.get_category_breakdown(user_id)

    # Get weekly trends (SQL aggregation - fast)
    weekly_data = db_service.get_weekly_expenses(user_id, weeks=4)

    # Get only recent transactions for display (not all)
    recent_transactions = db_service.get_recent_transactions(user_id, limit=10)

    return render_template('dashboard_modern.html',
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance,
                         transactions=recent_transactions,
                         category_data=category_list,
                         weekly_data=weekly_data,
                         currency_symbol=currency_symbol)

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            date = request.form['date']
            description = request.form['description'].strip()
            category = request.form.get('category', '').strip()
            trans_type = request.form['type']

            # AI categorization with caching (fast)
            if not category:
                try:
                    category, confidence = ml_service.categorize_transaction(description)
                    if confidence < 0.6:
                        category = None
                except:
                    category = None

            # Create transaction
            db_service.create_transaction(
                user_id=session['user_id'],
                amount=amount,
                date=date,
                description=description,
                category=category,
                type=trans_type
            )

            flash('Transaction added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid amount. Please enter a valid number.', 'error')
            return redirect(url_for('add_transaction'))
        except Exception as e:
            flash(f'Error adding transaction: {str(e)}', 'error')
            return redirect(url_for('add_transaction'))

    return render_template('add_transaction_modern.html')

@app.route('/transactions')
@login_required
def transactions():
    """Transactions page with pagination"""
    user_id = session['user_id']
    
    # Get page from query params
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get paginated transactions
    offset = (page - 1) * per_page
    all_transactions = db_service.get_user_transactions(user_id, limit=per_page, offset=offset)
    
    # Get total count for pagination
    summary = db_service.get_user_transactions_summary(user_id)
    total_count = summary['total_count'] or 0
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('transactions_modern.html',
                         transactions=all_transactions,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count)

@app.route('/reports')
@login_required
def reports():
    """Optimized reports page"""
    user_id = session['user_id']
    
    # Get summary
    summary = db_service.get_user_transactions_summary(user_id)
    
    # Get monthly trends (SQL aggregation)
    monthly_data = db_service.get_monthly_expenses(user_id, months=6)
    
    # Get category breakdown
    category_breakdown = db_service.get_category_breakdown(user_id)
    
    return render_template('reports_modern.html',
                         total_income=summary['total_income'] or 0,
                         total_expenses=summary['total_expenses'] or 0,
                         monthly_data=monthly_data,
                         category_breakdown=category_breakdown)

@app.route('/api/ml/categorize', methods=['POST'])
@login_required
def api_categorize():
    """Fast ML categorization API with caching"""
    data = request.get_json()
    description = data.get('description', '')

    try:
        category, confidence = ml_service.categorize_transaction(description)
        return jsonify({
            'category': category,
            'confidence': float(confidence)
        })
    except Exception as e:
        return jsonify({'error': 'AI service unavailable', 'details': str(e)}), 500

@app.route('/api/transactions', methods=['GET', 'POST'])
@login_required
def api_transactions():
    """API for transactions with pagination"""
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page
        
        transactions = db_service.get_user_transactions(
            session['user_id'], 
            limit=per_page, 
            offset=offset
        )
        return jsonify(transactions)
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            transaction = db_service.create_transaction(
                user_id=session['user_id'],
                amount=data['amount'],
                date=data['date'],
                description=data.get('description', ''),
                category=data.get('category'),
                type=data.get('type', 'Expense')
            )
            return jsonify(transaction), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@login_required
def api_delete_transaction(transaction_id):
    """Delete transaction API"""
    if db_service.delete_transaction(transaction_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Transaction not found'}), 404

@app.route('/search')
@login_required
def search_transactions():
    """Search transactions"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('transactions'))
    
    results = db_service.search_transactions(session['user_id'], query, limit=50)
    return render_template('transactions_modern.html', 
                         transactions=results,
                         search_query=query)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        currency = request.form.get('currency', '$')
        from database.setup_postgres import update_user_profile
        update_user_profile(session['user_id'], currency_symbol=currency)
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    user_profile = get_user_profile(session['user_id'])
    currency_symbol = user_profile.get('currency_symbol', '$') if user_profile else '$'
    
    return render_template('settings_modern.html', currency_symbol=currency_symbol)


def create_app():
    """Factory function for creating the app"""
    return app


if __name__ == '__main__':
    print("="*60)
    print("EXPENSE TRACKER - OPTIMIZED VERSION")
    print("="*60)
    print("\nPerformance optimizations:")
    print("  ✓ Connection pooling (2-10 connections)")
    print("  ✓ ML prediction caching")
    print("  ✓ Aggregated SQL queries")
    print("  ✓ Pagination for large datasets")
    print("  ✓ Lazy loading of transactions")
    print("\nStarting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
