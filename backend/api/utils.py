from .models import LeaderboardEntry
import random

def add_score_delta(player_name, delta):
    """
    Add a delta (positive or negative) to a player's score.
    
    Args:
        player_name (str): The name of the player
        delta (int): The amount to add/subtract from the score
    
    Returns:
        dict: Result with success status and details
    """
    try:
        # Try to find the player by name (case-insensitive)
        player = LeaderboardEntry.objects.filter(name__iexact=player_name).first()
        
        if not player:
            return {
                'success': False,
                'error': f'Player "{player_name}" not found'
            }
        
        old_score = player.score
        player.score += delta
        
        # Ensure score doesn't go below 0
        if player.score < 0:
            player.score = 0
        
        player.save()
        
        return {
            'success': True,
            'player': player.name,
            'old_score': old_score,
            'new_score': player.score,
            'delta': delta
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def increase_score(player_name, amount):
    """
    Increase a player's score by a specific amount.
    
    Args:
        player_name (str): The name of the player
        amount (int): The amount to increase the score by
    
    Returns:
        dict: Result with success status and details
    """
    return add_score_delta(player_name, amount)

def decrease_score(player_name, amount):
    """
    Decrease a player's score by a specific amount.
    
    Args:
        player_name (str): The name of the player
        amount (int): The amount to decrease the score by
    
    Returns:
        dict: Result with success status and details
    """
    return add_score_delta(player_name, -amount)

def random_score_increase(player_name, min_amount=100, max_amount=200):
    """
    Increase a player's score by a random amount within a range.
    
    Args:
        player_name (str): The name of the player
        min_amount (int): Minimum amount to increase
        max_amount (int): Maximum amount to increase
    
    Returns:
        dict: Result with success status and details
    """
    random_delta = random.randint(min_amount, max_amount)
    return add_score_delta(player_name, random_delta)

def get_player_score(player_name):
    """
    Get a player's current score.
    
    Args:
        player_name (str): The name of the player
    
    Returns:
        dict: Result with success status and score
    """
    try:
        player = LeaderboardEntry.objects.filter(name__iexact=player_name).first()
        
        if not player:
            return {
                'success': False,
                'error': f'Player "{player_name}" not found'
            }
        
        return {
            'success': True,
            'player': player.name,
            'score': player.score
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }