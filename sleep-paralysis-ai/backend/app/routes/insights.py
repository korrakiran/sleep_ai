"""
Insights Routes (Sarvam AI Version)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..ml.ai_service import analyze_with_ai

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate():
    """Generate intelligent AI insights from features using Sarvam AI"""
    data = request.get_json()
    features = {
        'stress_level': float(data.get('stress_level', 5)),
        'watched_horror': bool(data.get('watched_horror', False)),
        'screen_time': float(data.get('screen_time', 4)),
        'sleep_hours': float(data.get('sleep_hours', 7)),
        'caffeine_intake': float(data.get('caffeine_intake', 0)),
        'physical_activity': float(data.get('physical_activity', 0)),
        'sleep_position': data.get('sleep_position', 'back'),
        'bedtime_hour': float(data.get('bedtime_hour', 23)),
        'nap_taken': bool(data.get('nap_taken', False))
    }
    
    # We call the full analysis but just return the insights part
    result = analyze_with_ai(features)
    if result:
        return jsonify({'insights': result['insights']}), 200
    return jsonify({'error': 'AI Service unavailable'}), 503

@insights_bp.route('/tips', methods=['GET'])
def general_tips():
    """Return general sleep paralysis prevention tips"""
    tips = [
        {
            'category': 'Sleep Hygiene',
            'tips': [
                'Maintain a consistent sleep schedule, even on weekends.',
                'Sleep on your side instead of your back.',
                'Keep your bedroom cool (18-20°C) and dark.',
                'Avoid screens 1 hour before bed.'
            ]
        },
        {
            'category': 'Stress Management',
            'tips': [
                'Practice 4-7-8 breathing before bed.',
                'Journal your worries to offload mental burden.',
                'Meditate for 10 minutes to lower cortisol.',
                'Avoid stimulating conversations or content before sleep.'
            ]
        },
        {
            'category': 'During an Episode',
            'tips': [
                'Remain calm — sleep paralysis is not dangerous.',
                'Focus on wiggling one finger or toe to break the paralysis.',
                'Control your breathing to avoid panic.',
                'You will regain control within 1-2 minutes.'
            ]
        }
    ]
    return jsonify({'tips': tips}), 200
