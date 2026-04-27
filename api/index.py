import sys
import os

# Add the project subfolder to the Python path
# On Vercel, everything is in /var/task/
project_root = os.path.dirname(os.path.dirname(__file__))
backend_path = os.path.join(project_root, 'sleep-paralysis-ai', 'backend')
sys.path.append(backend_path)

# Import the Flask app directly
# This MUST be top-level for Vercel to find it
from run import app

# Vercel needs the 'app' variable to be available at the module level
application = app
