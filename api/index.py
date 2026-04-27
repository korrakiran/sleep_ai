import sys
import os
import traceback

# Add the project subfolder to the Python path
project_path = os.path.join(os.path.dirname(__file__), '..', 'sleep-paralysis-ai', 'backend')
sys.path.append(project_path)

try:
    # Import the Flask app from your run.py
    from run import app
except Exception as e:
    # If the app fails to load, return the error as text so we can see it in the browser
    error_info = traceback.format_exc()
    from flask import Flask
    app = Flask(__name__)
    @app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_all(path):
        return f"BACKEND CRASH DURING BOOT:\n\n{error_info}", 500
