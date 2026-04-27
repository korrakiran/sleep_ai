"""
Authentication Routes (MongoDB Version)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId
from ..models.database import users_col

auth_bp = Blueprint('auth', __name__)

def user_to_dict(user):
    """Helper to convert MongoDB user doc to serializable dict"""
    if not user: return None
    return {
        'id': str(user['_id']),
        'name': user['name'],
        'email': user['email'],
        'age': user.get('age'),
        'created_at': user['created_at'].isoformat() if isinstance(user['created_at'], datetime) else user['created_at']
    }

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    data = request.get_json()

    # Validation
    required = ['name', 'email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # Check duplicate email
    if users_col.find_one({'email': data['email'].lower().strip()}):
        return jsonify({'error': 'Email already registered'}), 409

    # Create user document
    user_doc = {
        'name': data['name'].strip(),
        'email': data['email'].lower().strip(),
        'password_hash': generate_password_hash(data['password'], method='pbkdf2:sha256'),
        'age': data.get('age'),
        'created_at': datetime.utcnow()
    }
    
    result = users_col.insert_one(user_doc)
    user_doc['_id'] = result.inserted_id

    # Generate JWT token
    token = create_access_token(identity=str(user_doc['_id']))

    return jsonify({
        'message': 'Account created successfully',
        'token': token,
        'user': user_to_dict(user_doc)
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate existing user"""
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].lower().strip()
    user = users_col.find_one({'email': email})

    if not user or not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(user['_id']))

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user_to_dict(user)
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    user_id = get_jwt_identity()
    user = users_col.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user_to_dict(user)}), 200

@auth_bp.route('/anonymous', methods=['POST'])
def anonymous_login():
    """Create or resume an anonymous session"""
    data = request.get_json()
    device_id = data.get('device_id', 'global_guest')
    
    email = f"guest_{device_id}@sleep.ai"
    user = users_col.find_one({'email': email})
    
    if not user:
        user_doc = {
            'name': 'Guest User',
            'email': email,
            'password_hash': 'none',
            'is_anonymous': True,
            'created_at': datetime.utcnow()
        }
        result = users_col.insert_one(user_doc)
        user = user_doc
        user['_id'] = result.inserted_id
        
    token = create_access_token(identity=str(user['_id']))
    return jsonify({
        'token': token,
        'user': user_to_dict(user)
    }), 200
