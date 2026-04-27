import sys
import os

# Add the project subfolder to the Python path
project_path = os.path.join(os.path.dirname(__file__), '..', 'sleep-paralysis-ai', 'backend')
sys.path.append(project_path)

# Import the Flask app from your run.py
from run import app

# Vercel needs the 'app' variable to be available at the module level
# This bridge file ensures Vercel finds it instantly.
