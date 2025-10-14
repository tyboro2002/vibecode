from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import LeaderboardEntry
from .utils import random_score_increase
import json
import random

def add_cors_headers(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def get_random_avatar():
    """Return a random avatar emoji"""
    avatars = ['👩', '👨', '🧑', '👩‍💼', '👨‍💼', '👩‍🔬', '👨‍🔬', '👩‍💻', '👨‍💻', 
               '👩‍🏫', '👨‍🏫', '👩‍⚕️', '👨‍⚕️', '👩‍🎨', '👨‍🎨', '👩‍🚀', '👨‍🚀',
               '👩‍🌾', '👨‍🌾', '👩‍🍳', '👨‍🍳', '👩‍🎤', '👨‍🎤', '👩‍🎬', '👨‍🎬']
    return random.choice(avatars)

@csrf_exempt
def get_leaderboard(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({'success': True})
        return add_cors_headers(response)
    
    try:
        # Get all leaderboard entries ordered by score
        entries = LeaderboardEntry.objects.all()
        
        # Format data for frontend
        leaderboard_data = []
        for index, entry in enumerate(entries, 1):
            leaderboard_data.append({
                'rank': index,
                'name': entry.name,
                'score': entry.score,
                'avatar': get_random_avatar()
            })
        
        response = JsonResponse({
            'success': True,
            'leaderboard': leaderboard_data
        })
        return add_cors_headers(response)
        
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)

@csrf_exempt
def process_text(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({'success': True})
        return add_cors_headers(response)
    
    if request.method != 'POST':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)
    
    try:
        data = json.loads(request.body)
        input_text = data.get('text', '')
        
        # Increase Henry Davis's score randomly on each text submission
        henry_result = random_score_increase("Henry Davis", 100, 200)
        
        # Simple text processing - you can make this more sophisticated
        if not input_text.strip():
            response_text = "No text provided. Please enter some text to process."
        else:
            # Example processing: reverse the text, add some formatting
            processed_text = f"✨ Processed Text ✨\n\n"
            processed_text += f"Original length: {len(input_text)} characters\n"
            processed_text += f"Word count: {len(input_text.split())}\n"
            processed_text += f"Reversed: {input_text[::-1]}\n\n"
            processed_text += f"Uppercase: {input_text.upper()}\n\n"
            processed_text += f"Formatted:\n{'-' * 20}\n{input_text}\n{'-' * 20}"
            
            # Add Henry's score update info to the response
            if henry_result['success']:
                processed_text += f"\n\n🎉 Bonus Info:\n"
                processed_text += f"Henry Davis gained {henry_result['delta']} points!\n"
                processed_text += f"New score: {henry_result['new_score']} (was {henry_result['old_score']})"
            
            response_text = processed_text
        
        response_data = {
            'success': True,
            'processed_text': response_text,
            'original_text': input_text
        }
        
        # Include Henry's score update in the response
        if henry_result['success']:
            response_data['score_update'] = henry_result
        
        response = JsonResponse(response_data)
        return add_cors_headers(response)
        
    except json.JSONDecodeError:
        response = JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
        return add_cors_headers(response)
    
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)
