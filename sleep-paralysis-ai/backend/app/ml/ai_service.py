"""
Sarvam AI Service - Sleep Paralysis Intelligence
Uses Sarvam AI's LLM to analyze user data and provide predictions/insights.
"""
import os
import requests
import json

SARVAM_API_KEY = os.environ.get('SARVAM_API_KEY', 'your_sarvam_api_key_here')
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

def analyze_with_ai(features):
    """
    Send user features to Sarvam AI for expert health analysis.
    Returns structured JSON with risk_level, probability, episode_time, and insights.
    """
    prompt = f"""
    You are a Sleep Science AI Expert specializing in Sleep Paralysis.
    Analyze the following daytime behavior data for a user:
    - Stress Level: {features.get('stress_level')}/10
    - Watched Horror: {'Yes' if features.get('watched_horror') else 'No'}
    - Screen Time: {features.get('screen_time')} hours
    - Sleep Duration: {features.get('sleep_hours')} hours
    - Caffeine Intake: {features.get('caffeine_intake')} cups
    - Physical Activity: {features.get('physical_activity')} hours
    - Sleep Position: {features.get('sleep_position')}
    - Bedtime: {features.get('bedtime_hour')}:00
    - Daytime Nap: {'Yes' if features.get('nap_taken') else 'No'}

    Based on clinical research on sleep paralysis triggers, provide a detailed prediction in JSON format ONLY.
    The response must follow this EXACT structure:
    {{
        "risk_level": "Low" | "Medium" | "High",
        "risk_probability": float (0.0 to 1.0),
        "predicted_episode_time": "HH:MM",
        "rem_phase_start": "HH:MM",
        "insights": [
            {{
                "type": "warning" | "danger" | "success" | "info" | "caution",
                "icon": "Lucide icon name (e.g., 'alert-triangle', 'check-circle', 'shield', 'activity', 'moon')",
                "title": "Short Title",
                "message": "Specific actionable advice based on the data."
            }}
        ]
    }}
    Include 4-5 high-quality, personalized insights. If risk is High, explain why based on the combination of factors.
    """

    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": SARVAM_API_KEY  # Sarvam AI uses this header often or Authorization
    }
    
    # Try both common authentication methods for Sarvam
    auth_headers = [
        {"api-subscription-key": SARVAM_API_KEY},
        {"Authorization": f"Bearer {SARVAM_API_KEY}"}
    ]

    payload = {
        "model": "sarvam-2b", # or sarvam-1, check documentation for latest
        "messages": [
            {"role": "system", "content": "You are a specialized sleep paralysis expert AI. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        # We try the most likely header first
        response = requests.post(SARVAM_URL, headers=auth_headers[0], json=payload, timeout=30)
        
        # If 401/403, try the other header style
        if response.status_code in [401, 403]:
            response = requests.post(SARVAM_URL, headers=auth_headers[1], json=payload, timeout=30)

        if response.status_code != 200:
            print(f"[AI Service] Error from Sarvam AI: {response.text}")
            return None

        content = response.json()['choices'][0]['message']['content']
        
        # Strip any markdown code blocks if AI returns them
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        return json.loads(content.strip())

    except Exception as e:
        print(f"[AI Service] Exception: {str(e)}")
        return None
