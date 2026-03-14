# 💰 Budget Tracker - Modern Expense Management

A **simple, professional, and creative** budget tracking application with AI-powered expense categorization.

![Budget Tracker](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## ✨ Features

### 🎨 Modern UI/UX
- **Clean & Professional** - Simple, beautiful design
- **Mobile Responsive** - Works on all devices
- **Gradient Background** - Modern purple-to-pink gradient
- **Smooth Animations** - Delightful user experience

### 💵 Budget Tracking
- **Income - Expenses = Balance** - Real-time budget calculation
- **Visual Balance Display** - See remaining budget at a glance
- **Positive/Negative Indicators** - Know if you're over budget
- **Category Breakdown** - Track spending by category

### 🤖 AI-Powered
- **Auto-Categorization** - 84%+ accuracy
- **Real-time Suggestions** - As you type
- **15 Categories** - Comprehensive coverage
- **Smart Defaults** - Learns from your input

### 🔒 Secure
- **Password Hashing** - Werkzeug security
- **Session Management** - Flask-Login
- **SQLite Database** - Production-ready
- **User Authentication** - Secure login/register

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python backend/database/setup_db.py
```

### 3. Run Application
```bash
python backend/app.py
```

### 4. Open Browser
```
http://localhost:5000
```

---

## 📱 How to Use

### First Time Setup
1. **Register** - Create an account with username, email, password
2. **Login** - Sign in with your credentials
3. **Add Initial Budget** - Record your monthly salary or total budget
4. **Start Tracking** - Add expenses as you make them

### Daily Usage
1. **Login** to your account
2. **Dashboard** shows your current balance
3. **Add Transaction** when you spend or earn money
4. **View Transactions** to see history
5. **Check Reports** for spending insights

### Adding Transactions

#### For Income (Salary):
- Type: **Income**
- Amount: e.g., `5000`
- Description: "Monthly salary"
- Category: **Salary**
- Date: Today

#### For Expenses:
- Type: **Expense**
- Amount: e.g., `15.50`
- Description: "Starbucks coffee"
- Category: Auto-filled by AI (Food & Dining)
- Date: Today

---

## 🎨 UI Design

### Color Scheme
- **Primary**: Purple (#6366f1)
- **Success**: Green (#22c55e)
- **Danger**: Red (#ef4444)
- **Background**: Purple-Pink Gradient

### Category Colors
Each category has a unique pastel color for easy recognition:
- 🍔 Food & Dining - Amber
- 🚗 Transportation - Blue
- 🏠 Housing - Green
- 🎬 Entertainment - Purple
- 🏥 Healthcare - Red
- 🛍️ Shopping - Pink
- ✈️ Travel - Cyan
- 📚 Education - Indigo
- And 7 more...

---

## 📊 Features Breakdown

### Dashboard
- **Balance Display** - Large, prominent balance
- **3 Stat Cards** - Income, Expenses, Remaining
- **Category Chart** - Pie chart of spending
- **Trend Chart** - Spending over time
- **Recent Transactions** - Last 10 transactions

### Add Transaction
- **Type Selector** - Income or Expense
- **Amount Input** - With $ symbol
- **Description** - AI analyzes as you type
- **Category Dropdown** - Auto-filled or manual
- **Date Picker** - Default to today

### Transactions List
- **Full History** - All your transactions
- **Filter & Sort** - Coming soon
- **Edit/Delete** - Manage entries
- **Category Badges** - Color-coded

### Reports
- **Summary Stats** - Total income/expenses
- **Category Breakdown** - Where money goes
- **Charts** - Visual insights
- **Export** - CSV/Excel (optional)

---

## 🗄️ Database

### SQLite (Default)
- **File**: `backend/database/budget_tracker.db`
- **Tables**: users, user_profiles, categories, transactions, budgets
- **Auto-created** on first run

### PostgreSQL (Production)
```python
# Set environment variables
export DB_HOST=your-host
export DB_NAME=budget_tracker
export DB_USER=postgres
export DB_PASSWORD=your-password
```

---

## 🔐 Security

### Password Security
- Hashed with Werkzeug (PBKDF2)
- Minimum 6 characters
- Never stored in plain text

### Session Security
- Secure cookies
- 1-hour timeout
- CSRF protection

### Database Security
- Parameterized queries (SQL injection safe)
- Foreign key constraints
- Cascade deletes

---

## 🌐 Deployment

### Free Hosting Options

#### 1. PythonAnywhere (Recommended)
- **Free tier available**
- Easy setup
- SQLite support
- URL: `yourname.pythonanywhere.com`

#### 2. Railway
- **Free with limits**
- Auto-deploy from GitHub
- PostgreSQL included

#### 3. Render
- **Free tier**
- Easy deployment
- Good performance

See **DEPLOYMENT_GUIDE.md** for detailed instructions.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask
- **Database**: SQLite (dev), PostgreSQL (prod)
- **ML**: scikit-learn, pandas, numpy
- **Frontend**: Bootstrap 5, Chart.js
- **Icons**: Font Awesome
- **Auth**: Flask-Login, Werkzeug

---

## 📁 Project Structure

```
BudgetTracker/
├── backend/
│   ├── app.py                    # Main application
│   ├── database/
│   │   ├── setup_db.py           # Database initialization
│   │   └── budget_tracker.db     # SQLite database
│   ├── services/
│   │   ├── ml_service.py         # AI categorization
│   │   └── db_service.py         # Database operations
│   ├── ml_models/
│   │   └── robust_categorizer.py # ML model
│   ├── static/
│   │   └── css/
│   │       └── modern-theme.css  # Modern UI theme
│   └── templates/
│       ├── base_modern.html      # Base template
│       ├── login_modern.html     # Login page
│       ├── register_modern.html  # Register page
│       ├── dashboard_modern.html # Dashboard
│       ├── add_transaction_modern.html
│       └── transactions_modern.html
├── requirements.txt              # Dependencies
├── DEPLOYMENT_GUIDE.md          # Deployment instructions
└── README.md                    # This file
```

---

## 🧪 Testing

### Test AI Categorization
```python
from backend.services.ml_service import MLService

ml = MLService()
print(ml.categorize_transaction("starbucks coffee"))
# Output: ('Food & Dining', 0.91)
```

### Test Database
```bash
python backend/database/setup_db.py
```

### Test App Locally
```bash
python backend/app.py
# Visit http://localhost:5000
```

---

## 📈 Roadmap

### Coming Soon
- [ ] Budget limits per category
- [ ] Email notifications
- [ ] Recurring transactions
- [ ] Export to CSV/Excel
- [ ] Dark mode
- [ ] Multi-currency support
- [ ] Receipt scanning (OCR)
- [ ] Bank integration

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🆘 Support

### Common Issues

**Can't login?**
- Make sure database is initialized
- Check username/password
- Clear browser cache

**AI not working?**
- Check if model is trained
- Wait for model to load
- Check console for errors

**Database errors?**
- Delete `budget_tracker.db`
- Re-run `setup_db.py`
- Check file permissions

### Get Help
1. Check this README
2. Review DEPLOYMENT_GUIDE.md
3. Check application logs
4. Test locally first

---

## 🎉 Credits

- **Developer**: You!
- **ML Model**: Custom scikit-learn categorizer
- **UI Design**: Modern, minimal theme
- **Icons**: Font Awesome
- **Charts**: Chart.js

---

## 📊 Stats

- **Accuracy**: 84%+ AI categorization
- **Categories**: 15 expense types
- **Load Time**: < 2 seconds
- **Users**: Unlimited
- **Transactions**: Unlimited

---

**Enjoy tracking your budget! 💰**

Made with ❤️ using Python, Flask, and Machine Learning
