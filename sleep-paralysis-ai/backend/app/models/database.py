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

client = MongoClient(mongo_uri)
# Explicitly set the database name to sleep_ai
db_name = 'sleep_ai'
db = client[db_name]

print(f"[DB] Connected to cluster. Using database: {db_name}")

# Collections
users_col = db['users']
logs_col = db['daily_logs']
predictions_col = db['predictions']
alarms_col = db['alarms']

def init_db():
    """Initialize indexes if needed"""
    users_col.create_index("email", unique=True)
    logs_col.create_index([("user_id", 1), ("date", -1)])
    predictions_col.create_index([("user_id", 1), ("created_at", -1)])
    alarms_col.create_index([("user_id", 1), ("is_active", 1)])
    print("[DB] MongoDB initialized and indexes created.")
