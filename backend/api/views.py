from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from .models import LeaderboardEntry, Problem, TestCase
from .utils import random_score_increase
from .auth import login_required, get_current_user
import json
import random

def add_cors_headers(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def get_random_avatar():
    """Return a random avatar emoji (fallback)"""
    avatars = ['👩', '👨', '🧑', '👩‍💼', '👨‍💼', '👩‍🔬', '👨‍🔬', '👩‍💻', '👨‍💻', 
               '👩‍🏫', '👨‍🏫', '👩‍⚕️', '👨‍⚕️', '👩‍🎨', '👨‍🎨', '👩‍🚀', '👨‍🚀',
               '👩‍🌾', '👨‍🌾', '👩‍🍳', '👨‍🍳', '👩‍🎤', '👨‍🎤', '👩‍🎬', '👨‍🎬']
    return random.choice(avatars)

def get_or_create_user_leaderboard_entry(user_info):
    """
    Get or create a leaderboard entry for the authenticated user.
    If the user doesn't exist, create them with a default score of 100.
    """
    zauth_id = user_info.get('id')
    username = user_info.get('username', 'unknown')
    picture_url = user_info.get('picture')
    
    # Try to find existing entry by zauth_id
    entry = LeaderboardEntry.objects.filter(zauth_id=zauth_id).first()
    
    if not entry:
        # Create new entry with score of 100, using username as name
        entry = LeaderboardEntry.objects.create(
            name=username,
            score=100,
            zauth_id=zauth_id,
            picture_url=picture_url
        )
        print(f"Created new leaderboard entry for {username} (score: 100)")
    else:
        # Update picture URL if it changed
        if entry.picture_url != picture_url:
            entry.picture_url = picture_url
            entry.save()
            print(f"Updated picture URL for {username}")
    
    return entry

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
            # Use stored picture URL, or emoji fallback
            avatar_url = entry.picture_url
            
            leaderboard_data.append({
                'rank': index,
                'name': entry.name,
                'score': entry.score,
                'avatar': get_random_avatar() if not avatar_url else None,
                'avatar_url': avatar_url
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
@login_required
def process_text(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({'success': True})
        return add_cors_headers(response)
    
    if request.method != 'POST':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)
    
    try:
        # Get the current authenticated user
        user = get_current_user(request)
        username = user.get('username', 'Unknown')
        
        data = json.loads(request.body)
        input_text = data.get('text', '')
        
        # Increase the authenticated user's score randomly on each text submission
        score_result = random_score_increase(username, 100, 200)
        
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
            
            # Add user's score update info to the response
            if score_result['success']:
                processed_text += f"\n\n🎉 Score Update:\n"
                processed_text += f"You gained {score_result['delta']} points!\n"
                processed_text += f"New score: {score_result['new_score']} (was {score_result['old_score']})"
            
            # Add authenticated user info
            processed_text += f"\n\n👤 Processed by: {username}"
            if user.get('name'):
                processed_text += f" ({user['name']})"
            
            response_text = processed_text
        
        response_data = {
            'success': True,
            'processed_text': response_text,
            'original_text': input_text
        }
        
        # Include user's score update in the response
        if score_result['success']:
            response_data['score_update'] = score_result
        
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


@csrf_exempt
def get_all_problems(request):
    if request.method != 'GET':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        problems = Problem.objects.all()
        problems_data = list(problems.values())
        response = JsonResponse({
            'success': True,
            'problems': problems_data
        })
        return add_cors_headers(response)
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)


@csrf_exempt
@login_required
def get_solved_problems(request):
    if request.method != 'GET':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Get the current authenticated user
        user = get_current_user(request)
        user_entry = get_or_create_user_leaderboard_entry(user)

        # Find all problems the user has solved (has at least one correct submission)
        from .models import Submission
        solved_problem_ids = Submission.objects.filter(
            submisser=user_entry,
            submission_correct=True
        ).values_list('problem_id', flat=True).distinct()

        response = JsonResponse({
            'success': True,
            'solved_problem_ids': list(solved_problem_ids)
        })
        return add_cors_headers(response)
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)


@csrf_exempt
@login_required
def generate_code(request):
    if request.method != 'POST':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        code = data.get('code', '')

        # Call external code generation service
        response = requests.post('http://llm:5555', json={
            'prompt': prompt, 'code': code
        })

        result = response.json()
        generated_code = result.get('code', '')

        response = JsonResponse({
            'success': True,
            'generated_code': generated_code
        })
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


@csrf_exempt
@login_required
def test_problem(request):
    if request.method != 'POST':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        submission_content = data.get('submission')

        # Get the current authenticated user
        user = get_current_user(request)
        user_entry = get_or_create_user_leaderboard_entry(user)

        # Fetch the problem
        problem = Problem.objects.filter(id=problem_id).first()
        if not problem:
            response = JsonResponse({
                'success': False,
                'error': 'Problem not found'
            }, status=404)
            return add_cors_headers(response)

        # Send submission to external grading service
        testcases = TestCase.objects.filter(problem_id=problem_id)
        
        # Serialize test cases with JSON input_data
        testcases_data = [
            {
                'id': tc.id,
                'input_data': tc.input_data,  # Already JSON, no need to parse
                'expected_output': tc.expected_output,
                'is_public': tc.is_public
            }
            for tc in testcases
        ]

        response = requests.post('http://grader:5556', json={
            'problem_id': problem_id,
            'code': submission_content,
            'tests': testcases_data
        })

        result = response.json()
        is_correct = result.get('correct', False)
        total_tests = result.get('total_tests', 0)
        passed_tests = result.get('passed_tests', 0)

        # Create submission record
        from .models import Submission
        submission = Submission.objects.create(
            problem=problem,
            submission_correct=is_correct,
            submisser=user_entry
        )

        # If all tests passed, award points to the user
        if total_tests > 0 and total_tests == passed_tests:
            # Check if user has already solved this problem before
            previous_correct = Submission.objects.filter(
                problem=problem,
                submisser=user_entry,
                submission_correct=True
            ).exclude(id=submission.id).exists()
            
            # Only award points if this is the first time solving
            if not previous_correct:
                user_entry.score += problem.points
                user_entry.save()

        response = JsonResponse({
            'success': True,
            'problem_id': problem_id,
            'submission_correct': is_correct,
            'results': result.get('results', []),
            'total_tests': total_tests,
            'passed_tests': passed_tests
        })
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
