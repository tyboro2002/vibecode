from django.urls import path
from . import views, auth_views

urlpatterns = [
    # Existing endpoints
    path('process-text/', views.process_text, name='process_text'),
    path('leaderboard/', views.get_leaderboard, name='get_leaderboard'),

    path('problems/all/', views.get_all_problems, name='get_all_problems'),

    path('submit/', views.generate_code, name='generate_code'),

    path('test/', views.test_problem, name='test'),
    
    # Authentication endpoints
    path('auth/login', auth_views.login, name='auth_login'),
    path('auth/callback', auth_views.callback, name='auth_callback'),
    path('auth/logout', auth_views.logout, name='auth_logout'),
    path('auth/profile', auth_views.get_profile, name='auth_profile'),
    path('auth/check', auth_views.check_auth, name='auth_check'),
    path('auth/test', auth_views.test_route, name='auth_test'),
    path('auth/debug', auth_views.debug_token, name='auth_debug'),
]