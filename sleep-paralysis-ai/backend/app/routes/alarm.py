"""
Smart Alarm Routes (MongoDB Version)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from ..models.database import alarms_col

alarm_bp = Blueprint('alarm', __name__)

def alarm_to_dict(alarm):
    """Helper to convert MongoDB alarm doc to serializable dict"""
    if not alarm: return None
    return {
        'id': str(alarm['_id']),
        'user_id': str(alarm['user_id']),
        'prediction_id': str(alarm.get('prediction_id')) if alarm.get('prediction_id') else None,
        'alarm_time': alarm['alarm_time'],
        'label': alarm.get('label', 'Sleep Paralysis Prevention Alarm'),
        'is_active': alarm.get('is_active', True),
        'triggered': alarm.get('triggered', False),
        'created_at': alarm['created_at'].isoformat() if isinstance(alarm['created_at'], datetime) else alarm['created_at']
    }

@alarm_bp.route('/', methods=['GET'])
@jwt_required()
def get_alarms():
    """Get all active alarms for the user"""
    user_id = get_jwt_identity()
    cursor = alarms_col.find({'user_id': ObjectId(user_id), 'is_active': True}).sort('created_at', -1)
    alarms = [alarm_to_dict(a) for a in cursor]

    return jsonify({
        'alarms': alarms,
        'count': len(alarms)
    }), 200

@alarm_bp.route('/create', methods=['POST'])
@jwt_required()
def create_alarm():
    """Manually create a custom alarm"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('alarm_time'):
        return jsonify({'error': 'alarm_time is required (HH:MM)'}), 400

    alarm_doc = {
        'user_id': ObjectId(user_id),
        'alarm_time': data['alarm_time'],
        'label': data.get('label', 'Sleep Paralysis Prevention Alarm'),
        'is_active': True,
        'triggered': False,
        'created_at': datetime.utcnow()
    }
    
    result = alarms_col.insert_one(alarm_doc)
    alarm_doc['_id'] = result.inserted_id

    return jsonify({
        'message': 'Alarm created',
        'alarm': alarm_to_dict(alarm_doc)
    }), 201

@alarm_bp.route('/<string:alarm_id>/dismiss', methods=['PUT'])
@jwt_required()
def dismiss_alarm(alarm_id):
    """Dismiss/deactivate an alarm"""
    user_id = get_jwt_identity()
    result = alarms_col.find_one_and_update(
        {'_id': ObjectId(alarm_id), 'user_id': ObjectId(user_id)},
        {'$set': {'is_active': False, 'triggered': True}},
        return_document=True
    )
    
    if not result:
        return jsonify({'error': 'Alarm not found'}), 404
        
    return jsonify({'message': 'Alarm dismissed', 'alarm': alarm_to_dict(result)}), 200

@alarm_bp.route('/<string:alarm_id>', methods=['DELETE'])
@jwt_required()
def delete_alarm(alarm_id):
    """Delete an alarm"""
    user_id = get_jwt_identity()
    result = alarms_col.delete_one({'_id': ObjectId(alarm_id), 'user_id': ObjectId(user_id)})
    
    if result.deleted_count == 0:
        return jsonify({'error': 'Alarm not found'}), 404
        
    return jsonify({'message': 'Alarm deleted'}), 200
