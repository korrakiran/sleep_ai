"""
MongoDB Configuration for Sleep Paralysis AI
Using PyMongo for database operations
"""
import os
from pymongo import MongoClient

# Initialize MongoDB Client
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/sleep_paralysis')
sanitized_uri = mongo_uri.split('@')[-1] if '@' in mongo_uri else 'localhost'
print(f"[DB] Initializing connection to: {sanitized_uri}")

db_name = 'sleep_ai'

import time

# ... (rest of imports)

for i in range(3):
    try:
        # Use a short timeout for the initial connection to avoid hanging
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Trigger a connection check
        client.admin.command('ping')
        db = client[db_name]
        users_col = db['users']
        logs_col = db['daily_logs']
        predictions_col = db['predictions']
        alarms_col = db['alarms']
        print(f"[DB] Successfully connected to {db_name} (Attempt {i+1})")
        break
    except Exception as e:
        print(f"[DB] Connection Attempt {i+1} failed: {str(e)}")
        if i == 2: # Last attempt
            print(f"[DB] CRITICAL ERROR: Could not connect to MongoDB after 3 attempts.")
            db = None
            users_col = None
            logs_col = None
            predictions_col = None
            alarms_col = None
        else:
            time.sleep(1) # Wait a bit before retrying

def init_db():
    """Initialize indexes if needed"""
    if db is None:
        print("[DB] Skipping index creation: Database not connected.")
        return
    try:
        users_col.create_index("email", unique=True)
        logs_col.create_index([("user_id", 1), ("date", -1)])
        predictions_col.create_index([("user_id", 1), ("created_at", -1)])
        alarms_col.create_index([("user_id", 1), ("is_active", 1)])
        print("[DB] MongoDB initialized and indexes created.")
    except Exception as e:
        print(f"[DB] Index creation failed: {e}")
