from django.urls import path
from . import views

urlpatterns = [
    path('process-text/', views.process_text, name='process_text'),
    path('leaderboard/', views.get_leaderboard, name='get_leaderboard'),
]