# Deployment Guide - Budget Tracker

## 🚀 Deploy for Public Use

### Option 1: PythonAnywhere (FREE - Recommended for beginners)

#### Step 1: Create Account
1. Go to https://www.pythonanywhere.com
2. Sign up for a free account
3. Choose "Beginner" plan

#### Step 2: Upload Code
1. Go to **Files** tab
2. Create directory structure:
   ```
   /home/yourusername/
   └── BudgetTracker/
       ├── backend/
       │   ├── app.py
       │   ├── database/
       │   │   └── setup_db.py
       │   ├── services/
       │   ├── ml_models/
       │   ├── static/
       │   └── templates/
       └── requirements.txt
   ```

#### Step 3: Configure Web App
1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Python version: **3.10**
5. Set paths:
   - Source code: `/home/yourusername/BudgetTracker/backend`
   - Working directory: `/home/yourusername/BudgetTracker/backend`

#### Step 4: Install Dependencies
1. Open **Bash console**
2. Run:
   ```bash
   cd BudgetTracker
   pip install -r requirements.txt
   ```

#### Step 5: Configure WSGI
1. Edit WSGI configuration file
2. Replace with:
   ```python
   import sys
   path = '/home/yourusername/BudgetTracker'
   if path not in sys.path:
       sys.path.append(path)
   
   from backend.app import create_app
   application = create_app()
   ```

#### Step 6: Database Setup
1. Go to **Databases** tab
2. Initialize SQLite database in console:
   ```bash
   cd BudgetTracker/backend
   python database/setup_db.py
   ```

#### Step 7: Reload
1. Go back to **Web** tab
2. Click **Reload** button
3. Your app is live! 🎉

**Your URL**: `https://yourusername.pythonanywhere.com`

---

### Option 2: Heroku (FREE tier discontinued, but still good for paid)

#### Step 1: Prepare Files

Create `Procfile`:
```
web: gunicorn backend.app:app
```

Create `runtime.txt`:
```
python-3.10.0
```

#### Step 2: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

#### Step 3: Deploy
```bash
# Login
heroku login

# Create app
heroku create your-budget-tracker

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Open app
heroku open
```

---

### Option 3: Railway (FREE with limits)

1. Go to https://railway.app
2. Sign up with GitHub
3. Create new project
4. Connect your GitHub repo
5. Deploy automatically!

---

### Option 4: Render (FREE)

1. Go to https://render.com
2. Sign up
3. Create **Web Service**
4. Connect repository
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn backend.app:app`
7. Deploy!

---

## 🔧 Database Configuration for Production

### SQLite (Default - Good for small apps)
Already configured! Database file will be created at:
```
backend/database/budget_tracker.db
```

### PostgreSQL (Recommended for production)

1. Install psycopg2:
```bash
pip install psycopg2-binary
```

2. Update `database/setup_db.py`:
```python
import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'budget_tracker'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', ''),
        port=os.environ.get('DB_PORT', '5432')
    )
```

3. Set environment variables on your hosting platform

---

## 🔐 Security Checklist for Production

- [ ] Change `SECRET_KEY` in app.py
- [ ] Use HTTPS (automatic on most platforms)
- [ ] Set strong passwords
- [ ] Enable database backups
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets

---

## 📊 Monitoring & Maintenance

### Check Logs
- **PythonAnywhere**: Logs tab
- **Heroku**: `heroku logs --tail`
- **Railway**: Logs tab
- **Render**: Logs tab

### Database Backup
```bash
# SQLite
cp backend/database/budget_tracker.db backup.db

# PostgreSQL
pg_dump your_database_url > backup.sql
```

---

## 🎯 Quick Start Commands

### Local Testing
```bash
cd "D:\PFAI LAB\Expense_Budget_WebApp"
python backend/database/setup_db.py
python backend/app.py
```

### Access locally
```
http://localhost:5000
```

---

## 📱 Features Available

✅ User Registration & Login
✅ Dashboard with Balance Tracking
✅ Add Income/Expenses
✅ AI Auto-Categorization
✅ Transaction History
✅ Reports & Analytics
✅ Mobile Responsive
✅ Secure Authentication

---

## 🆘 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Database locked" error
Delete the database file and reinitialize:
```bash
rm backend/database/budget_tracker.db
python backend/database/setup_db.py
```

### Port already in use
Change port in app.py:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## 📞 Support

For issues or questions:
1. Check logs on your hosting platform
2. Test locally first
3. Verify all dependencies are installed
4. Check database permissions

---

**Ready to deploy! 🚀**

Choose your hosting platform and follow the steps above.
