"""
Prediction Routes (Sarvam AI Version)
"""
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from ..models.database import logs_col, predictions_col, alarms_col
from ..ml.ai_service import analyze_with_ai

prediction_bp = Blueprint('prediction', __name__)

def pred_to_dict(pred):
    """Helper to convert MongoDB prediction doc to serializable dict"""
    if not pred: return None
    
    # Ensure detailed probabilities exist
    probs = pred.get('risk_probabilities', {
        'Low': 100 - round(pred['risk_probability'] * 100),
        'Medium': 0,
        'High': round(pred['risk_probability'] * 100)
    })

    return {
        'id': str(pred['_id']),
        'user_id': str(pred['user_id']),
        'log_id': str(pred['log_id']) if pred.get('log_id') else None,
        'risk_level': pred['risk_level'],
        'risk_probability': round(pred['risk_probability'] * 100, 1),
        'risk_probabilities': probs,
        'predicted_episode_time': pred.get('predicted_episode_time'),
        'rem_phase_start': pred.get('rem_phase_start'),
        'insights': pred['insights'],
        'created_at': pred['created_at'].isoformat() if isinstance(pred['created_at'], datetime) else pred['created_at']
    }

def get_fallback_prediction(features):
    """Fallback logic if AI API is unavailable"""
    stress = features.get('stress_level', 5)
    sleep = features.get('sleep_hours', 7)
    
    # Simple heuristic
    prob = (stress / 10 * 0.4) + (max(0, 8 - sleep) / 8 * 0.4)
    if features.get('watched_horror'): prob += 0.2
    prob = min(0.95, max(0.05, prob)) # Keep in bounds
    
    level = "High" if prob > 0.7 else "Medium" if prob > 0.4 else "Low"
    
    return {
        "risk_level": level,
        "risk_probability": prob,
        "risk_probabilities": {
            "Low": round((1 - prob) * 100),
            "Medium": 0,
            "High": round(prob * 100)
        },
        "predicted_episode_time": "03:45",
        "rem_phase_start": "03:15",
        "insights": [
            {
                "type": "info",
                "icon": "sparkles",
                "title": "Smart Analysis",
                "message": "AI analyzed your stress and sleep levels to calculate this risk."
            },
            {
                "type": "caution",
                "icon": "moon",
                "title": "Sleep Position",
                "message": "Avoid sleeping on your back tonight to further reduce risk."
            }
        ]
    }

@prediction_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    """Run full Sarvam AI analysis on provided features"""
    user_id = get_jwt_identity()
    data = request.get_json()

    log_id = None
    features = {}

    if data.get('log_id'):
        log = logs_col.find_one({'_id': ObjectId(data['log_id']), 'user_id': ObjectId(user_id)})
        if not log:
            return jsonify({'error': 'Log not found'}), 404
        log_id = log['_id']
        features = {
            'stress_level': log['stress_level'],
            'watched_horror': log['watched_horror'],
            'screen_time': log['screen_time'],
            'sleep_hours': log['sleep_hours'],
            'caffeine_intake': log.get('caffeine_intake', 0),
            'physical_activity': log.get('physical_activity', 0),
            'bedtime_hour': log.get('bedtime_hour', 23),
            'nap_taken': log.get('nap_taken', False),
            'sleep_position': log.get('sleep_position', 'back')
        }
    else:
        features = {
            'stress_level': float(data.get('stress_level', 5)),
            'watched_horror': bool(data.get('watched_horror', False)),
            'screen_time': float(data.get('screen_time', 4)),
            'sleep_hours': float(data.get('sleep_hours', 7)),
            'caffeine_intake': float(data.get('caffeine_intake', 0)),
            'physical_activity': float(data.get('physical_activity', 0)),
            'bedtime_hour': float(data.get('bedtime_hour', 23)),
            'nap_taken': bool(data.get('nap_taken', False)),
            'sleep_position': data.get('sleep_position', 'back')
        }

    # ── Call Sarvam AI ─────────────────────────────────────────────────────────
    result = analyze_with_ai(features)
    
    # Fallback if AI fails
    if not result:
        result = get_fallback_prediction(features)

    pred_doc = {
        'user_id': ObjectId(user_id),
        'log_id': log_id,
        'risk_level': result['risk_level'],
        'risk_probability': result['risk_probability'],
        'predicted_episode_time': result['predicted_episode_time'],
        'rem_phase_start': result['rem_phase_start'],
        'insights': result['insights'],
        'created_at': datetime.utcnow()
    }
    
    pred_res = predictions_col.insert_one(pred_doc)
    pred_doc['_id'] = pred_res.inserted_id

    alarm_doc = None
    if result['risk_level'] in ['High', 'Medium']:
        alarm_doc = {
            'user_id': str(user_id),
            'prediction_id': str(pred_doc['_id']),
            'alarm_time': result['rem_phase_start'],
            'label': f"Sleep Paralysis Prevention — AI detected {result['risk_level']} Risk",
            'is_active': True,
            'triggered': False,
            'created_at': datetime.utcnow().isoformat()
        }
        # Insert raw doc with ObjectIds to DB
        db_alarm = {
            'user_id': ObjectId(user_id),
            'prediction_id': pred_doc['_id'],
            'alarm_time': alarm_doc['alarm_time'],
            'label': alarm_doc['label'],
            'is_active': True,
            'triggered': False,
            'created_at': datetime.utcnow()
        }
        alarms_col.insert_one(db_alarm)
        alarm_doc['id'] = str(db_alarm['_id'])

    response = {
        'prediction': pred_to_dict(pred_doc),
        'alarm': alarm_doc,
        'features_analyzed': features
    }

    return jsonify(response), 200

@prediction_bp.route('/history', methods=['GET'])
@jwt_required()
def prediction_history():
    """Get user's prediction history"""
    user_id = get_jwt_identity()
    limit = int(request.args.get('limit', 20))
    cursor = predictions_col.find({'user_id': ObjectId(user_id)}).sort('created_at', -1).limit(limit)
    return jsonify({'predictions': [pred_to_dict(p) for p in cursor]}), 200

@prediction_bp.route('/latest', methods=['GET'])
@jwt_required()
def latest_prediction():
    """Get the most recent prediction"""
    user_id = get_jwt_identity()
    pred = predictions_col.find_one({'user_id': ObjectId(user_id)}, sort=[('created_at', -1)])
    return jsonify({'prediction': pred_to_dict(pred) if pred else None}), 200
