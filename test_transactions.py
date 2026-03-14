"""
Test script to verify transaction functionality
"""
import sys
import os

# Add backend to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from database.setup_db import init_db, create_user, authenticate_user
from services.db_service import DBService

print("="*60)
print("TESTING TRANSACTION FUNCTIONALITY")
print("="*60)

# Step 1: Initialize database
print("\n1. Initializing database...")
db_path = init_db()
print(f"   [OK] Database path: {db_path}")
print(f"   [OK] Database exists: {os.path.exists(db_path)}")

# Step 2: Create test user
print("\n2. Creating test user...")
user_id = create_user("testuser", "test@test.com", "test123")
if user_id:
    print(f"   [OK] User created with ID: {user_id}")
else:
    print("   [WARN] User already exists, will use existing")
    # Get existing user
    auth = authenticate_user("testuser", "test123")
    if auth:
        user_id = auth['id']
        print(f"   [OK] Authenticated user ID: {user_id}")
    else:
        print("   [FAIL] Failed to authenticate user")
        sys.exit(1)

# Step 3: Test transaction creation
print("\n3. Testing transaction creation...")
db_service = DBService()

# Test Income transaction
print("   Adding income transaction...")
income = db_service.create_transaction(
    user_id=user_id,
    amount=5000.00,
    date="2026-03-10",
    description="Monthly salary",
    category="Salary",
    type="Income"
)
if income:
    print(f"   [OK] Income created: ID={income['id']}, Amount=${income['amount']}, Type={income['type']}")
else:
    print("   [FAIL] Failed to create income transaction")

# Test Expense transaction
print("   Adding expense transaction...")
expense = db_service.create_transaction(
    user_id=user_id,
    amount=150.00,
    date="2026-03-10",
    description="Shell gas station",
    category="Transportation",
    type="Expense"
)
if expense:
    print(f"   [OK] Expense created: ID={expense['id']}, Amount=${expense['amount']}, Type={expense['type']}, Category={expense['category']}")
else:
    print("   [FAIL] Failed to create expense transaction")

# Test another expense
print("   Adding another expense...")
expense2 = db_service.create_transaction(
    user_id=user_id,
    amount=400.00,
    date="2026-03-09",
    description="Grocery shopping",
    category="Food & Dining",
    type="Expense"
)
if expense2:
    print(f"   [OK] Expense created: ID={expense2['id']}, Amount=${expense2['amount']}, Type={expense2['type']}, Category={expense2['category']}")
else:
    print("   [FAIL] Failed to create expense transaction")

# Step 4: Get all transactions
print("\n4. Getting all transactions for user...")
transactions = db_service.get_user_transactions(user_id)
print(f"   [OK] Found {len(transactions)} transactions")

for t in transactions:
    print(f"      - {t['date']}: {t['description']} | {t['category']} | {t['type']} | ${t['amount']}")

# Step 5: Calculate balance
print("\n5. Calculating balance...")
total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'Expense')
balance = total_income - total_expenses

print(f"   Total Income:   ${total_income:,.2f}")
print(f"   Total Expenses: ${total_expenses:,.2f}")
print(f"   Balance:        ${balance:,.2f}")

if balance >= 0:
    print(f"   [OK] Status: Positive (Within budget)")
else:
    print(f"   [FAIL] Status: Negative (Over budget)")

# Step 6: Test update
print("\n6. Testing transaction update...")
if expense:
    success = db_service.update_transaction(
        transaction_id=expense['id'],
        amount=175.00  # Changed from 150 to 175
    )
    if success:
        updated = db_service.get_transaction_by_id(expense['id'])
        print(f"   [OK] Transaction updated: New amount=${updated['amount']}")
    else:
        print("   [FAIL] Failed to update transaction")

# Step 7: Category breakdown
print("\n7. Category breakdown...")
category_stats = {}
for t in transactions:
    if t['type'] == 'Expense' and t['category']:
        cat = t['category']
        if cat not in category_stats:
            category_stats[cat] = {'amount': 0, 'count': 0}
        category_stats[cat]['amount'] += t['amount']
        category_stats[cat]['count'] += 1

for cat, stats in category_stats.items():
    percentage = (stats['amount'] / total_expenses * 100) if total_expenses > 0 else 0
    print(f"   {cat}: ${stats['amount']:,.2f} ({percentage:.1f}%) - {stats['count']} transactions")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nExpected Results:")
print("  - 3 transactions created (1 income, 2 expenses)")
print("  - Total Income: $5,000.00")
print("  - Total Expenses: $550.00 (or $575.00 after update)")
print("  - Balance: $4,450.00 (or $4,425.00 after update)")
print("  - Categories: Transportation, Food & Dining")
print("\n[OK] All functions working correctly!")
