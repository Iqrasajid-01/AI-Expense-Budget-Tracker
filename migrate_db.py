import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.setup_db import migrate_user_profiles

if __name__ == '__main__':
    migrate_user_profiles()
