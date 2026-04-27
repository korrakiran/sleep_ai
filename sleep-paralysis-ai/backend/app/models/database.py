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
    print(f"[DB] Successfully connected to {db_name}")
except Exception as e:
    print(f"[DB] CRITICAL ERROR: Could not connect to MongoDB: {str(e)}")
    # We don't exit so the app can still serve a 500 error instead of hanging
    db = None
    users_col = None
    logs_col = None
    predictions_col = None
    alarms_col = None

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
