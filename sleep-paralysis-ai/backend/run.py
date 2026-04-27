import os
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)
print(f"[BOOT] Loading .env from: {env_path}")

from app import create_app

# Create Flask app
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
