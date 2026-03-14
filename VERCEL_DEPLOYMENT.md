# Vercel Deployment Guide

## Files Created for Vercel

1. **`api/index.py`** - Vercel serverless entry point
2. **`vercel.json`** - Vercel configuration file
3. **`runtime.txt`** - Python version specification
4. **`.python-version`** - Python version for Vercel
5. **`.vercelignore`** - Files to exclude from deployment

## Deployment Steps

### 1. Push to GitHub
First, commit and push all files to your GitHub repository:
```bash
git add .
git commit -m "Configure for Vercel deployment"
git push
```

### 2. Deploy via Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your Git repository
4. Click "Deploy"

### 3. Deploy via Vercel CLI (Alternative)
```bash
npm install -g vercel
vercel login
vercel
```

## Project Structure for Vercel

```
Expense_Budget_WebApp/
├── api/
│   └── index.py          # Vercel entry point
├── backend/
│   ├── app.py            # Main Flask app
│   ├── templates/        # HTML templates
│   ├── static/           # CSS, JS files
│   ├── database/         # SQLite database
│   ├── models/           # Data models
│   └── services/         # Business logic
├── vercel.json           # Vercel configuration
├── runtime.txt           # Python version
├── .python-version       # Python version
├── requirements.txt      # Python dependencies
└── .vercelignore         # Files to exclude
```

## Configuration Details

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.11",
        "installCommand": "rm -f pyproject.toml && pip install -r requirements.txt"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

**Key Configuration:**
- `installCommand`: Removes `pyproject.toml` and forces pip usage (prevents uv errors)
- `runtime`: Specifies Python 3.11

### Files Excluded from Deployment (.vercelignore)
- Test files (`test_*.py`)
- Cache files (`__pycache__/`)
- IDE files (`.idea/`, `.vscode/`)
- Demo and debug files

## Important Notes

### Database (⚠️ Critical)
- **SQLite is used** for the database
- On Vercel, the database is stored in `/tmp/budget_tracker/`
- **⚠️ Warning**: Vercel serverless functions are stateless
  - The database will be **reset** on each deployment
  - Data may be lost after function cold starts
  - For production, consider migrating to PostgreSQL:
    - [Neon](https://neon.tech) (Serverless PostgreSQL)
    - [Supabase](https://supabase.com)
    - [Railway](https://railway.app)

### Environment Variables
Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | A random secure string (e.g., `my-super-secret-key-12345`) |

### Limitations
- **Serverless timeout**: 10 seconds on Hobby plan
- **Cold starts**: First request after inactivity may be slow
- **File system**: Read-only except `/tmp` directory
- **Database persistence**: Not guaranteed with SQLite

## Troubleshooting

### "No Python version specified"
✅ Fixed: Added `.python-version` and `runtime.txt` files

### "No `project` table found in pyproject.toml"
✅ Fixed: `installCommand` removes `pyproject.toml` before installing

### "Failed to run uv lock"
✅ Fixed: Using `pip install -r requirements.txt` instead of uv

### Test files appearing in build logs
✅ Fixed: Added test files to `.vercelignore`

### Database errors on Vercel
- Database is stored in `/tmp/` which is writable
- Data will be lost on redeployment
- For persistent data, migrate to PostgreSQL

## Local Testing

Test the Vercel configuration locally:
```bash
vercel dev
```

## Production Deployment

```bash
vercel --prod
```

## Post-Deployment Checklist

- [ ] Set `SECRET_KEY` environment variable
- [ ] Test user registration
- [ ] Test login/logout
- [ ] Add a transaction
- [ ] Check dashboard displays correctly
- [ ] Verify currency settings work
- [ ] Test reports page

## Migrating to PostgreSQL (Recommended for Production)

1. **Add PostgreSQL dependency**:
   ```bash
   echo "psycopg2-binary==2.9.9" >> requirements.txt
   ```

2. **Update database connection** in `backend/database/setup_db.py`:
   ```python
   import os
   import psycopg2
   
   def get_db_connection():
       if os.environ.get('VERCEL'):
           # Use environment variable for PostgreSQL
           return psycopg2.connect(os.environ['DATABASE_URL'])
       else:
           # Use SQLite for local development
           return sqlite3.connect(get_db_path())
   ```

3. **Set `DATABASE_URL`** in Vercel environment variables

4. **Deploy a PostgreSQL database** on:
   - [Neon](https://neon.tech) (Free tier available)
   - [Supabase](https://supabase.com)
   - [Railway](https://railway.app)
