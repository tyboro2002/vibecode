"""
Zeus OAuth Authentication Module

This module provides OAuth authentication using Zeus' zauth system.
"""

import tomllib
from pathlib import Path
from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from authlib.integrations.requests_client import OAuth2Session
import requests

# Load configuration
config_path = Path(settings.BASE_DIR) / 'config.toml'
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

ZAUTH_CONFIG = config['zauth']


def get_oauth_session(token=None, state=None):
    """
    Create and return an OAuth2Session for Zeus authentication.
    
    Args:
        token: Optional token dict for authenticated requests
        state: Optional state parameter for CSRF protection
    
    Returns:
        OAuth2Session configured for Zeus
    """
    return OAuth2Session(
        client_id=ZAUTH_CONFIG['client_id'],
        client_secret=ZAUTH_CONFIG['client_secret'],
        authorization_endpoint=ZAUTH_CONFIG['authorize_url'],
        token_endpoint=ZAUTH_CONFIG['access_token_url'],
        redirect_uri=ZAUTH_CONFIG['redirect_uri'],
        scope=ZAUTH_CONFIG['scope'],
        token=token,
        state=state,
    )


def get_user_info(access_token):
    """
    Fetch user information from Zeus API using the access token.
    
    Args:
        access_token: The OAuth access token
    
    Returns:
        dict: User information from Zeus
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Try multiple endpoints - Zeus might use different paths
    endpoints = [
        f"https://zauth.zeus.gent/current_user"
    ]
    
    errors = []
    
    for endpoint in endpoints:
        try:
            print(f"Trying endpoint: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✓ Successfully fetched user info from: {endpoint}")
                print(f"User data: {user_data}")
                return user_data
            else:
                error_msg = f"{response.status_code} - {response.text[:200]}"
                errors.append(f"{endpoint}: {error_msg}")
                print(f"✗ Failed at {endpoint}: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            errors.append(f"{endpoint}: {error_msg}")
            print(f"✗ Exception at {endpoint}: {error_msg}")
            continue
    
    # All endpoints failed
    full_error = "\n".join(errors)
    raise Exception(f"Failed to fetch user info from all endpoints:\n{full_error}")


def login_required(view_func):
    """
    Decorator to require authentication for a view.
    
    Returns 401 if user is not authenticated.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user' not in request.session:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'login_url': '/api/auth/login'
            }, status=401)
        return view_func(request, *args, **kwargs)
    
    wrapper.__name__ = view_func.__name__
    return wrapper


def get_current_user(request):
    """
    Get the current authenticated user from the session.
    
    Args:
        request: Django request object
    
    Returns:
        dict: User information or None if not authenticated
    """
    return request.session.get('user')


def is_authenticated(request):
    """
    Check if the current request is authenticated.
    
    Args:
        request: Django request object
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    return 'user' in request.session and 'oauth_token' in request.session
