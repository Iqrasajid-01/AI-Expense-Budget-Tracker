# Personalized Budget Planning and Expense Categorization System

A web-based budget planning system with ML-powered expense categorization and predictive budgeting. The system features OOP-based backend with Flask, SQLite database, and ML models for automated expense classification and budget forecasting.

## Features

- **Expense Tracking**: Add, view, edit, and delete financial transactions
- **Automatic Categorization**: ML-powered expense categorization with ≥80% accuracy
- **Budget Prediction**: Forecast weekly, monthly, and yearly budgets based on historical spending
- **Interactive Dashboards**: Visualize spending patterns and trends
- **User Authentication**: Secure login and user profile management
- **Data Import/Export**: Support for CSV and Excel formats

## Technology Stack

- **Backend**: Python 3.x with Flask
- **ML**: scikit-learn, pandas, numpy
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript with Bootstrap and Chart.js
- **Authentication**: Flask-Login

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```bash
   python backend/database/init_db.py
   ```

6. Run the application:
   ```bash
   python backend/app.py
   ```

7. Access the application at `http://localhost:5000`

## Usage

1. Register a new account or log in if you already have one
2. Add your first transaction using the "Add Transaction" form
3. View your dashboard to see spending summaries and budget adherence
4. Generate reports to analyze spending patterns over time

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── models/                # Data models (UserProfile, Transaction, etc.)
│   ├── __init__.py
│   ├── user_profile.py
│   ├── transaction.py
│   ├── category_manager.py
│   └── budget_planner.py
├── services/              # Business logic services
│   ├── ml_service.py
│   ├── db_service.py
│   └── auth_service.py
├── ml_models/             # ML model implementations and training scripts
│   ├── expense_categorizer.py
│   ├── budget_predictor.py
│   ├── trained_models/
│   └── training_data/
├── static/                # CSS, JS, and image assets
├── templates/             # HTML templates
├── database/              # Database schema and migrations
└── tests/                 # Unit and integration tests
```

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Transactions
- `GET /transactions` - Get user transactions
- `POST /transactions` - Create a new transaction
- `GET /transactions/{id}` - Get a specific transaction
- `PUT /transactions/{id}` - Update a specific transaction
- `DELETE /transactions/{id}` - Delete a specific transaction

### Categories
- `GET /categories` - Get all categories
- `POST /categories` - Create a new category

### Reports
- `GET /reports` - View reports and analytics
- `GET /api/reports/summary` - Get financial summary (API)
- `GET /api/reports/export` - Export transactions

### ML Services
- `POST /api/ml/categorize` - Categorize a transaction description
- `POST /api/ml/predict-budget` - Predict budget based on historical data

## Machine Learning Models

### Expense Categorization
- Uses Logistic Regression with TF-IDF vectorization
- Achieves ≥80% accuracy for automatic categorization
- Handles transaction descriptions to assign categories

### Budget Prediction
- Uses Linear Regression with polynomial features
- Generates predictions for weekly, monthly, and yearly timeframes
- Analyzes historical spending patterns for forecasting

## Database Schema

The system uses SQLite with the following main tables:
- `user_profiles` - Stores user account information
- `transactions` - Stores individual transactions
- `categories` - Stores expense/income categories
- `budgets` - Stores budget information
- `ml_models` - Tracks ML model information

## Testing

To run the tests:
```bash
python -m pytest tests/
```

## Security Features

- Password hashing using Werkzeug security
- Session management with Flask-Login
- Input validation and sanitization
- SQL injection prevention through parameterized queries
- CSRF protection

## Performance Goals

- ML categorization completes within 1 second
- Budget predictions generate within 3 seconds
- Dashboard and report pages load within 3 seconds for datasets up to 1000 transactions
- System can handle at least 10,000 transactions per user without performance degradation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.