"""
Authentication views for Zeus OAuth integration
"""

from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .auth import (
    get_oauth_session, 
    get_user_info, 
    get_current_user,
    is_authenticated,
    ZAUTH_CONFIG
)

url = "http://localhost:5173"
# url = "http://192.168.0.107:5173"

@csrf_exempt
@require_http_methods(["GET", "POST"])
def login(request):
    """
    Initiate the OAuth login flow by redirecting to Zeus authorization URL.
    """
    try:
        oauth = get_oauth_session()
        authorization_url, state = oauth.create_authorization_url(
            ZAUTH_CONFIG['authorize_url']
        )
        
        # Store state in session for CSRF protection
        request.session['oauth_state'] = state
        
        # Return the authorization URL for frontend to redirect
        if request.method == 'GET':
            return redirect(authorization_url)
        else:  # POST - return JSON for AJAX requests
            return JsonResponse({
                'success': True,
                'authorization_url': authorization_url
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to initiate login',
            'details': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def callback(request):
    """
    Handle the OAuth callback from Zeus.
    Exchange the authorization code for an access token and fetch user info.
    """
    try:
        # Get the authorization response URL
        authorization_response = request.build_absolute_uri()
        
        # Retrieve the state from session
        state = request.session.get('oauth_state')
        
        # Create OAuth session and fetch token
        oauth = get_oauth_session(state=state)
        token = oauth.fetch_token(
            url=ZAUTH_CONFIG['access_token_url'],
            authorization_response=authorization_response,
            client_secret=ZAUTH_CONFIG['client_secret']
        )
        
        print(f"Token received. Keys: {token.keys()}")
        print(f"Token contents: {token}")
        
        # Try to get user info - first check if it's in the token response
        user_info = None
        
        # Some OAuth providers include user info in the token response
        if 'user' in token:
            user_info = token['user']
            print("User info found in token response")
        elif 'userinfo' in token:
            user_info = token['userinfo']
            print("Userinfo found in token response")
        else:
            # Fetch user information from API using the standard userinfo endpoint
            userinfo_url = f"{ZAUTH_CONFIG['api_base_url']}/user"
            print(f"Trying to fetch user info from: {userinfo_url}")
            
            try:
                user_info = get_user_info(token['access_token'])
                print(f"User info retrieved successfully: {user_info}")
            except Exception as user_error:
                # Log the full error and fail authentication
                print(f"ERROR: Failed to fetch user info: {user_error}")
                print(f"Token access_token present: {'access_token' in token}")
                
                # Instead of creating a fake user, return an error
                import urllib.parse
                error_msg = urllib.parse.quote(f"Failed to get user info: {str(user_error)}")
                return redirect(f'{url}/?login=error&message={error_msg}')
        
        # Store user info and token in session
        request.session['user'] = user_info
        request.session['oauth_token'] = token
        
        # Create or update leaderboard entry for this user
        from .views import get_or_create_user_leaderboard_entry
        try:
            get_or_create_user_leaderboard_entry(user_info)
        except Exception as e:
            print(f"Warning: Failed to create/update leaderboard entry: {e}")
        
        # Clean up state
        request.session.pop('oauth_state', None)
        
        # For web flow, redirect to frontend
        frontend_url = request.GET.get('redirect', '/')
        
        # Redirect to frontend with success (you might want to customize this URL)
        return redirect(f'{url}{frontend_url}?login=success')
        
    except Exception as e:
        # Better error handling - redirect to frontend with error
        import urllib.parse
        error_msg = urllib.parse.quote(str(e))
        return redirect(f'{url}/?login=error&message={error_msg}')


@csrf_exempt
@require_http_methods(["GET", "POST"])
def logout(request):
    """
    Logout the user by clearing the session.
    """
    try:
        request.session.pop('user', None)
        request.session.pop('oauth_token', None)
        request.session.flush()
        
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to logout',
            'details': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_profile(request):
    """
    Get the current user's profile information.
    """
    if not is_authenticated(request):
        return JsonResponse({
            'success': False,
            'error': 'Not authenticated',
            'authenticated': False
        }, status=401)
    
    try:
        user = get_current_user(request)
        return JsonResponse({
            'success': True,
            'authenticated': True,
            'user': user
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch profile',
            'details': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def check_auth(request):
    """
    Check if the user is currently authenticated.
    """
    authenticated = is_authenticated(request)
    
    response_data = {
        'success': True,
        'authenticated': authenticated
    }
    
    if authenticated:
        user = get_current_user(request)
        response_data['user'] = {
            'id': user.get('id'),
            'username': user.get('username'),
            'name': user.get('name', user.get('username')),
            'picture': user.get('picture'),
        }
    
    return JsonResponse(response_data)


@csrf_exempt
@require_http_methods(["GET"])
def test_route(request):
    """
    Simple test route to verify the auth system is working.
    """
    return JsonResponse({
        'success': True,
        'message': 'Auth system is working!',
        'authenticated': is_authenticated(request)
    })


@csrf_exempt
@require_http_methods(["GET"])
def debug_token(request):
    """
    Debug endpoint to check token and user info.
    Only use in development!
    """
    if not is_authenticated(request):
        return JsonResponse({
            'authenticated': False,
            'message': 'Not authenticated'
        })
    
    token = request.session.get('oauth_token', {})
    user = request.session.get('user', {})
    
    # Don't expose the full token for security
    return JsonResponse({
        'authenticated': True,
        'has_access_token': 'access_token' in token,
        'token_type': token.get('token_type'),
        'user_keys': list(user.keys()) if user else [],
        'username': user.get('username', 'N/A'),
        'name': user.get('name', 'N/A'),
    })
