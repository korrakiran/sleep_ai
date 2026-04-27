"""
Daily Activity Tracker Routes (MongoDB Version)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from bson import ObjectId
from ..models.database import logs_col

tracker_bp = Blueprint('tracker', __name__)

def log_to_dict(log):
    """Helper to convert MongoDB log doc to serializable dict"""
    if not log: return None
    return {
        'id': str(log['_id']),
        'user_id': str(log['user_id']),
        'date': log['date'].isoformat() if hasattr(log['date'], 'isoformat') else log['date'],
        'stress_level': log['stress_level'],
        'watched_horror': log['watched_horror'],
        'screen_time': log['screen_time'],
        'sleep_hours': log['sleep_hours'],
        'caffeine_intake': log.get('caffeine_intake', 0.0),
        'physical_activity': log.get('physical_activity', 0.0),
        'sleep_position': log.get('sleep_position', 'back'),
        'nap_taken': log.get('nap_taken', False),
        'bedtime_hour': log.get('bedtime_hour', 23.0),
        'created_at': log['created_at'].isoformat() if isinstance(log['created_at'], datetime) else log['created_at']
    }

@tracker_bp.route('/log', methods=['POST'])
@jwt_required()
def create_log():
    """Submit a new daily activity log"""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    required = ['stress_level', 'screen_time', 'sleep_hours']
    for field in required:
        if data.get(field) is None:
            return jsonify({'error': f'{field} is required'}), 400

    log_doc = {
        'user_id': ObjectId(user_id),
        'date': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
        'stress_level': float(data['stress_level']),
        'watched_horror': bool(data.get('watched_horror', False)),
        'screen_time': float(data['screen_time']),
        'sleep_hours': float(data['sleep_hours']),
        'caffeine_intake': float(data.get('caffeine_intake', 0.0)),
        'physical_activity': float(data.get('physical_activity', 0.0)),
        'sleep_position': data.get('sleep_position', 'back'),
        'nap_taken': bool(data.get('nap_taken', False)),
        'bedtime_hour': float(data.get('bedtime_hour', 23.0)),
        'created_at': datetime.utcnow()
    }

    result = logs_col.insert_one(log_doc)
    log_doc['_id'] = result.inserted_id

    return jsonify({
        'message': 'Daily log saved successfully',
        'log': log_to_dict(log_doc)
    }), 201

@tracker_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    """Get user's recent activity logs"""
    user_id = get_jwt_identity()
    limit = int(request.args.get('limit', 30))

    cursor = logs_col.find({'user_id': ObjectId(user_id)}).sort('created_at', -1).limit(limit)
    logs = [log_to_dict(log) for log in cursor]

    return jsonify({
        'logs': logs,
        'count': len(logs)
    }), 200

@tracker_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get aggregated statistics for dashboard"""
    user_id = get_jwt_identity()
    logs = list(logs_col.find({'user_id': ObjectId(user_id)}).sort('created_at', -1))

    if not logs:
        return jsonify({'stats': None, 'message': 'No data yet'}), 200

    total = len(logs)
    avg_stress = sum(l['stress_level'] for l in logs) / total
    avg_sleep = sum(l['sleep_hours'] for l in logs) / total
    avg_screen = sum(l['screen_time'] for l in logs) / total
    horror_count = sum(1 for l in logs if l['watched_horror'])

    return jsonify({
        'stats': {
            'total_logs': total,
            'avg_stress': round(avg_stress, 1),
            'avg_sleep_hours': round(avg_sleep, 1),
            'avg_screen_time': round(avg_screen, 1),
            'horror_exposure_count': horror_count,
            'horror_exposure_pct': round(horror_count / total * 100, 1)
        }
    }), 200
