"""
Seed script (MongoDB Version) — creates demo user and sample logs.
Run: python seed.py
"""
import sys, os
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from app.models.database import users_col, logs_col, db



def seed():
    # Clear existing data for demo user
    existing = users_col.find_one({'email': 'demo@sleep.ai'})
    if existing:
        user_id = existing['_id']
        users_col.delete_one({'_id': user_id})
        logs_col.delete_many({'user_id': user_id})
        print("Removed old demo user and logs.")

    # Create demo user
    user_doc = {
        'name': 'Demo User',
        'email': 'demo@sleep.ai',
        'password_hash': generate_password_hash('demo1234', method='pbkdf2:sha256'),
        'age': 25,
        'created_at': datetime.utcnow()
    }
    
    result = users_col.insert_one(user_doc)
    user_id = result.inserted_id
    print(f"Created demo user with ID: {user_id}")

    # Seed 14 days of logs
    logs = []
    for i in range(14):
        day = datetime.utcnow() - timedelta(days=14-i)
        log_doc = {
            'user_id': user_id,
            'date': day.replace(hour=0, minute=0, second=0, microsecond=0),
            'stress_level': round(random.uniform(3, 9), 1),
            'watched_horror': random.choice([True, False, False]),
            'screen_time': round(random.uniform(2, 10), 1),
            'sleep_hours': round(random.uniform(4, 9), 1),
            'caffeine_intake': round(random.uniform(0, 4), 1),
            'physical_activity': round(random.uniform(0, 2), 1),
            'sleep_position': random.choice(['back', 'side', 'side', 'stomach']),
            'nap_taken': random.choice([True, False, False]),
            'bedtime_hour': round(random.uniform(22, 25) % 24, 1),
            'created_at': day
        }
        logs.append(log_doc)
    
    if logs:
        logs_col.insert_many(logs)
        print(f"Seeded {len(logs)} daily logs.")

    print("✅ MongoDB Seeding Complete!")
    print("Demo Credentials: demo@sleep.ai / demo1234")

if __name__ == "__main__":
    seed()
