"""
Budget Tracker Application - Optimized
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

# Import database setup functions (always available)
from database.setup_postgres import init_db, create_user, authenticate_user, get_user_by_id, migrate_user_profiles, get_user_profile

def create_app():
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

    # Initialize optimized services (fast - uses pooling/caching)
    # Falls back to original services if optimized versions fail
    try:
        from services.db_service_optimized import DBService
        from services.ml_service_optimized import get_ml_service
        db_service = DBService()
        ml_service = get_ml_service()
        print("✓ Using optimized services (connection pooling + caching)")
    except Exception as e:
        print(f"⚠ Using standard services: {e}")
        from services.db_service_postgres import DBService
        from services.ml_service import MLService
        db_service = DBService()
        ml_service = MLService()

    # Initialize database (PostgreSQL)
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
            user.email = user_data['email']
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
                session['email'] = user_data['email']
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
        """Optimized dashboard - uses aggregated queries for speed"""
        user_id = session['user_id']

        # Get summary with single fast query (instead of loading all transactions)
        summary = db_service.get_user_transactions_summary(user_id)
        total_income = summary['total_income'] or 0
        total_expenses = summary['total_expenses'] or 0
        balance = summary['balance'] or 0

        # Get currency
        user_profile = get_user_profile(user_id)
        currency_symbol = user_profile.get('currency_symbol', '$') if user_profile else '$'

        # Get category breakdown (single optimized query)
        category_list = db_service.get_category_breakdown(user_id)

        # Get weekly trends (SQL aggregation - fast)
        weekly_data = db_service.get_weekly_expenses(user_id, weeks=4)

        # Get only recent transactions for display (not all - major speedup!)
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
                
                # If no category provided, use AI
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
            except Exception as e:
                flash(f'Error adding transaction: {str(e)}', 'error')
        
        return render_template('add_transaction_modern.html')
    
    @app.route('/transactions')
    @login_required
    def transactions():
        """Transactions page with pagination for speed"""
        user_id = session['user_id']
        
        # Get page from query params
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Get paginated transactions (fast - only loads 20 at a time)
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
        """Optimized reports page using aggregated queries"""
        user_id = session['user_id']
        
        # Get summary (single fast query)
        summary = db_service.get_user_transactions_summary(user_id)
        total_income = summary['total_income'] or 0
        total_expenses = summary['total_expenses'] or 0
        
        # Get currency
        user_profile = get_user_profile(user_id)
        currency_symbol = user_profile.get('currency_symbol', '$') if user_profile else '$'

        # Get category breakdown (single optimized query)
        category_breakdown = db_service.get_category_breakdown(user_id)
        
        # Calculate percentages
        for cat in category_breakdown:
            cat['percentage'] = (cat['amount'] / total_expenses * 100) if total_expenses > 0 else 0
        
        # Sort by amount (highest first)
        category_breakdown.sort(key=lambda x: x['amount'], reverse=True)
        
        # Monthly trends (last 6 months) - SQL aggregation (fast!)
        monthly_data = db_service.get_monthly_expenses(user_id, months=6)
        
        # Get recent transactions
        user_transactions = db_service.get_recent_transactions(user_id, limit=20)

        return render_template('reports_modern.html',
                             transactions=user_transactions,
                             total_income=total_income,
                             total_expenses=total_expenses,
                             category_breakdown=category_breakdown,
                             monthly_data=monthly_data,
                             currency_symbol=currency_symbol)
    
    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        user_id = session['user_id']
        
        # Get user profile data
        from database.setup_postgres import get_user_profile, update_user_profile, update_user_email
        user_profile = get_user_profile(user_id)
        
        if request.method == 'POST':
            # Handle profile update
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            currency = request.form.get('currency', 'USD').strip()
            
            # Update user profile
            if update_user_email(user_id, email):
                session['email'] = email
            
            if update_user_profile(user_id, currency=currency, first_name=first_name, last_name=last_name):
                flash('Profile updated successfully!', 'success')
            else:
                flash('Failed to update profile.', 'error')
            
            return redirect(url_for('settings'))
        
        transactions = db_service.get_user_transactions(user_id)

        total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'Expense')

        return render_template('settings_modern.html',
                             transactions=transactions,
                             total_income=total_income,
                             total_expenses=total_expenses,
                             user_profile=user_profile)

    @app.route('/save_preferences', methods=['POST'])
    @login_required
    def save_preferences():
        """Save user preferences (currency, theme, etc.)"""
        user_id = session['user_id']

        currency = request.form.get('currency', 'USD').strip()

        from database.setup_postgres import update_user_profile
        if update_user_profile(user_id, currency=currency):
            flash('Preferences saved successfully!', 'success')
        else:
            flash('Failed to save preferences.', 'error')

        return redirect(url_for('settings'))

    @app.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_transaction(id):
        transaction = db_service.get_transaction_by_id(id)
        
        if not transaction or transaction['user_id'] != session['user_id']:
            flash('Transaction not found', 'error')
            return redirect(url_for('transactions'))
        
        if request.method == 'POST':
            try:
                amount = float(request.form['amount'])
                date = request.form['date']
                description = request.form['description'].strip()
                category = request.form.get('category', '').strip()
                trans_type = request.form['type']
                
                db_service.update_transaction(
                    id,
                    amount=amount,
                    date=date,
                    description=description,
                    category=category,
                    type=trans_type
                )
                
                flash('Transaction updated successfully!', 'success')
                return redirect(url_for('transactions'))
            except Exception as e:
                flash(f'Error updating transaction: {str(e)}', 'error')
        
        return render_template('edit_transaction_modern.html', transaction=transaction)
    
    @app.route('/delete_transaction/<int:id>', methods=['POST'])
    @login_required
    def delete_transaction(id):
        transaction = db_service.get_transaction_by_id(id)
        
        if not transaction or transaction['user_id'] != session['user_id']:
            flash('Transaction not found', 'error')
            return redirect(url_for('transactions'))
        
        db_service.delete_transaction(id)
        flash('Transaction deleted successfully!', 'success')
        return redirect(url_for('transactions'))
    
    # API Routes
    
    @app.route('/api/ml/categorize', methods=['POST'])
    @login_required
    def api_categorize():
        data = request.get_json()
        description = data.get('description', '')

        try:
            category, confidence = ml_service.categorize_transaction(description)
            # Ensure confidence is a valid number
            if confidence is None or (isinstance(confidence, float) and (confidence != confidence)):  # NaN check
                confidence = 0.0
            return jsonify({
                'category': category,
                'confidence': float(confidence)
            })
        except Exception as e:
            import traceback
            print(f"ML categorization error: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': 'AI service unavailable', 'details': str(e)}), 500
    
    @app.route('/api/transactions', methods=['GET', 'POST'])
    @login_required
    def api_transactions():
        if request.method == 'GET':
            transactions = db_service.get_user_transactions(session['user_id'])
            return jsonify(transactions)
        
        elif request.method == 'POST':
            data = request.get_json()
            try:
                transaction = db_service.create_transaction(
                    user_id=session['user_id'],
                    amount=data['amount'],
                    date=data.get('date', str(datetime.now().date())),
                    description=data['description'],
                    category=data.get('category'),
                    type=data['type']
                )
                return jsonify(transaction), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 400
    
    @app.route('/api/transactions/<int:id>', methods=['DELETE'])
    @login_required
    def api_delete_transaction(id):
        transaction = db_service.get_transaction_by_id(id)
        
        if not transaction or transaction['user_id'] != session['user_id']:
            return jsonify({'error': 'Not found'}), 404
        
        db_service.delete_transaction(id)
        return jsonify({'message': 'Deleted successfully'})
    
    @app.route('/api/reports/summary', methods=['GET'])
    @login_required
    def api_report_summary():
        summary = db_service.get_financial_summary(session['user_id'])
        return jsonify(summary)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("BUDGET TRACKER - Starting Application")
    print("="*60)
    print("\nAccess the application at: http://localhost:5000")
    print("\nFeatures:")
    print("  ✓ Modern, professional UI")
    print("  ✓ AI-powered categorization (84%+ accuracy)")
    print("  ✓ Budget tracking (Income - Expenses)")
    print("  ✓ SQLite database for production")
    print("  ✓ Secure authentication")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
