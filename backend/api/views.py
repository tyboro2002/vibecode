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
                'id': entry.id,
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
# @login_required
def update_problem(request, problem_id):
    if request.method == 'OPTIONS':
        response = JsonResponse({'success': True})
        return add_cors_headers(response)
    
    if request.method != 'PATCH' and request.method != 'PUT':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Check if user is tyboro (admin check)
        user = get_current_user(request)
        username = user.get('username', '')
        
        if username != 'tyboro' or username != 'runo' :
            response = JsonResponse({
                'success': False,
                'error': 'Unauthorized - Admin access required'
            }, status=403)
            return add_cors_headers(response)

        # Get the problem
        problem = Problem.objects.filter(id=problem_id).first()
        
        if not problem:
            response = JsonResponse({
                'success': False,
                'error': 'Problem not found'
            }, status=404)
            return add_cors_headers(response)

        # Parse request data
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'points' in data:
            problem.points = data['points']
        
        if 'assignment' in data:
            problem.assignment = data['assignment']
        
        if 'name' in data:
            problem.name = data['name']
        
        problem.save()
        
        response = JsonResponse({
            'success': True,
            'problem': {
                'id': problem.id,
                'name': problem.name,
                'points': problem.points,
                'assignment': problem.assignment
            }
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
# @login_required
def create_test(request):
    if request.method != 'POST':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)
    
    try:
        # # Admin check
        # user = get_current_user(request)
        # if user.username != 'tyboro' or username != 'runo' :
        #     response = JsonResponse({
        #         'success': False,
        #         'error': 'Unauthorized - Admin access required'
        #     }, status=403)
        #     return add_cors_headers(response)
        
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        input_data = data.get('input_data')
        expected_output = data.get('expected_output')
        is_public = data.get('is_public', True)
        
        if not problem_id or input_data is None or expected_output is None:
            response = JsonResponse({
                'success': False,
                'error': 'Missing required fields: problem_id, input_data, expected_output'
            }, status=400)
            return add_cors_headers(response)
        
        # Verify problem exists
        from .models import Problem
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            response = JsonResponse({
                'success': False,
                'error': f'Problem with id {problem_id} not found'
            }, status=404)
            return add_cors_headers(response)
        
        # Create the test case
        test_case = TestCase.objects.create(
            problem=problem,
            input_data=input_data,
            expected_output=expected_output,
            is_public=is_public
        )
        
        response = JsonResponse({
            'success': True,
            'test': {
                'id': test_case.id,
                'problem_id': test_case.problem.id,
                'problem_name': test_case.problem.name,
                'input_data': test_case.input_data,
                'expected_output': test_case.expected_output,
                'is_public': test_case.is_public
            }
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
# @login_required
def delete_test(request, test_id):
    if request.method != 'DELETE':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)
    
    try:
        # Admin check
        # user = get_current_user(request)
        # if user.username != 'tyboro' or username != 'runo' :
        #     response = JsonResponse({
        #         'success': False,
        #         'error': 'Unauthorized - Admin access required'
        #     }, status=403)
        #     return add_cors_headers(response)
        
        # Find the test case
        try:
            test_case = TestCase.objects.get(id=test_id)
        except TestCase.DoesNotExist:
            response = JsonResponse({
                'success': False,
                'error': f'Test case with id {test_id} not found'
            }, status=404)
            return add_cors_headers(response)
        
        test_case.delete()
        
        response = JsonResponse({
            'success': True,
            'message': f'Test case {test_id} deleted successfully'
        })
        return add_cors_headers(response)
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)


@csrf_exempt
# @login_required
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
def get_user_solved_problems(request, user_id):
    if request.method != 'GET':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Get the user's leaderboard entry
        user_entry = LeaderboardEntry.objects.filter(id=user_id).first()
        
        if not user_entry:
            response = JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
            return add_cors_headers(response)

        # Find all problems the user has solved
        from .models import Submission
        solved_submissions = Submission.objects.filter(
            submisser=user_entry,
            submission_correct=True
        ).values_list('problem_id', flat=True).distinct()

        # Get the problem details
        solved_problems = Problem.objects.filter(id__in=solved_submissions).values('id', 'name', 'points')
        
        total_points = sum(p['points'] for p in solved_problems)

        response = JsonResponse({
            'success': True,
            'user_name': user_entry.name,
            'total_score': user_entry.score,
            'solved_problems': list(solved_problems),
            'total_points_from_problems': total_points,
            'problems_solved_count': len(solved_problems)
        })
        return add_cors_headers(response)
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)


@csrf_exempt
def get_all_tests(request):
    if request.method != 'GET':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Get all test cases with their associated problem information
        testcases = TestCase.objects.select_related('problem').all()
        
        testcases_data = []
        for tc in testcases:
            testcases_data.append({
                'id': tc.id,
                'problem_id': tc.problem.id,
                'problem_name': tc.problem.name,
                'input_data': tc.input_data,
                'expected_output': tc.expected_output,
                'is_public': tc.is_public
            })
        
        response = JsonResponse({
            'success': True,
            'tests': testcases_data,
            'total_count': len(testcases_data)
        })
        return add_cors_headers(response)
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)


@csrf_exempt
# @login_required
def update_test(request, test_id):
    if request.method == 'OPTIONS':
        response = JsonResponse({'success': True})
        return add_cors_headers(response)
    
    if request.method != 'PATCH' and request.method != 'PUT':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Check if user is tyboro (admin check)
        user = get_current_user(request)
        username = user.get('username', '')
        
        # if username != 'tyboro' or username != 'runo' :
        #     response = JsonResponse({
        #         'success': False,
        #         'error': 'Unauthorized - Admin access required'
        #     }, status=403)
        #     return add_cors_headers(response)

        # Get the test case
        test_case = TestCase.objects.filter(id=test_id).first()
        
        if not test_case:
            response = JsonResponse({
                'success': False,
                'error': 'Test case not found'
            }, status=404)
            return add_cors_headers(response)

        # Parse request data
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'is_public' in data:
            test_case.is_public = data['is_public']
        
        if 'expected_output' in data:
            test_case.expected_output = data['expected_output']
        
        if 'input_data' in data:
            test_case.input_data = data['input_data']
        
        test_case.save()
        
        response = JsonResponse({
            'success': True,
            'test': {
                'id': test_case.id,
                'problem_id': test_case.problem.id,
                'problem_name': test_case.problem.name,
                'input_data': test_case.input_data,
                'expected_output': test_case.expected_output,
                'is_public': test_case.is_public
            }
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


@csrf_exempt
def get_all_users(request):
    if request.method != 'GET':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Get all users with their submission counts
        from .models import Submission
        users = LeaderboardEntry.objects.all()
        
        users_data = []
        for user in users:
            total_submissions = Submission.objects.filter(submisser=user).count()
            correct_submissions = Submission.objects.filter(submisser=user, submission_correct=True).count()
            
            users_data.append({
                'id': user.id,
                'name': user.name,
                'score': user.score,
                'zauth_id': user.zauth_id,
                'picture_url': user.picture_url,
                'created_at': user.created_at.isoformat(),
                'total_submissions': total_submissions,
                'correct_submissions': correct_submissions
            })
        
        response = JsonResponse({
            'success': True,
            'users': users_data,
            'total_count': len(users_data)
        })
        return add_cors_headers(response)
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)


@csrf_exempt
def update_user(request, user_id):
    if request.method == 'OPTIONS':
        response = JsonResponse({'success': True})
        return add_cors_headers(response)
    
    if request.method != 'PATCH' and request.method != 'PUT':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Get the user
        user_entry = LeaderboardEntry.objects.filter(id=user_id).first()
        
        if not user_entry:
            response = JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
            return add_cors_headers(response)

        # Parse request data
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'score' in data:
            user_entry.score = data['score']
        
        user_entry.save()
        
        response = JsonResponse({
            'success': True,
            'user': {
                'id': user_entry.id,
                'name': user_entry.name,
                'score': user_entry.score,
                'zauth_id': user_entry.zauth_id,
                'picture_url': user_entry.picture_url
            }
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
def get_user_submissions(request, user_id):
    if request.method != 'GET':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Get the user's leaderboard entry
        user_entry = LeaderboardEntry.objects.filter(id=user_id).first()
        
        if not user_entry:
            response = JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
            return add_cors_headers(response)

        # Get all submissions for this user
        from .models import Submission
        submissions = Submission.objects.filter(submisser=user_entry).select_related('problem').order_by('-submission_time')
        
        submissions_data = []
        for submission in submissions:
            submissions_data.append({
                'id': submission.id,
                'problem_id': submission.problem.id,
                'problem_name': submission.problem.name,
                'problem_points': submission.problem.points,
                'submission_time': submission.submission_time.isoformat(),
                'submission_correct': submission.submission_correct
            })
        
        response = JsonResponse({
            'success': True,
            'user_name': user_entry.name,
            'user_score': user_entry.score,
            'submissions': submissions_data,
            'total_submissions': len(submissions_data)
        })
        return add_cors_headers(response)
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)


@csrf_exempt
# @login_required
def update_submission(request, submission_id):
    if request.method == 'OPTIONS':
        response = JsonResponse({'success': True})
        return add_cors_headers(response)
    
    if request.method != 'PATCH' and request.method != 'PUT':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)

    try:
        # Find the submission
        from .models import Submission
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            response = JsonResponse({
                'success': False,
                'error': f'Submission with id {submission_id} not found'
            }, status=404)
            return add_cors_headers(response)

        # Parse request data
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'submission_correct' in data:
            submission.submission_correct = data['submission_correct']
        
        submission.save()
        
        response = JsonResponse({
            'success': True,
            'submission': {
                'id': submission.id,
                'problem_id': submission.problem.id,
                'problem_name': submission.problem.name,
                'problem_points': submission.problem.points,
                'submission_time': submission.submission_time.isoformat(),
                'submission_correct': submission.submission_correct
            }
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
# @login_required
def delete_submission(request, submission_id):
    if request.method != 'DELETE':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        return add_cors_headers(response)
    
    try:
        # Find the submission
        from .models import Submission
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            response = JsonResponse({
                'success': False,
                'error': f'Submission with id {submission_id} not found'
            }, status=404)
            return add_cors_headers(response)
        
        submission.delete()
        
        response = JsonResponse({
            'success': True,
            'message': f'Submission {submission_id} deleted successfully'
        })
        return add_cors_headers(response)
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)
