from django.core.management.base import BaseCommand
from api.utils import add_score_delta, increase_score, decrease_score, random_score_increase, get_player_score

class Command(BaseCommand):
    help = 'Test the score utility functions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing score utility functions...\n'))
        
        # Test get_player_score
        self.stdout.write('1. Getting Henry Davis current score:')
        result = get_player_score("Henry Davis")
        if result['success']:
            self.stdout.write(f"   Current score: {result['score']}")
        else:
            self.stdout.write(f"   Error: {result['error']}")
        
        # Test random_score_increase
        self.stdout.write('\n2. Testing random score increase (100-200):')
        result = random_score_increase("Henry Davis", 100, 200)
        if result['success']:
            self.stdout.write(f"   {result['player']}: {result['old_score']} → {result['new_score']} (+{result['delta']})")
        else:
            self.stdout.write(f"   Error: {result['error']}")
        
        # Test specific increase
        self.stdout.write('\n3. Testing specific score increase (+50):')
        result = increase_score("Henry Davis", 50)
        if result['success']:
            self.stdout.write(f"   {result['player']}: {result['old_score']} → {result['new_score']} (+{result['delta']})")
        else:
            self.stdout.write(f"   Error: {result['error']}")
        
        # Test decrease
        self.stdout.write('\n4. Testing score decrease (-25):')
        result = decrease_score("Henry Davis", 25)
        if result['success']:
            self.stdout.write(f"   {result['player']}: {result['old_score']} → {result['new_score']} ({result['delta']})")
        else:
            self.stdout.write(f"   Error: {result['error']}")
        
        # Test with non-existent player
        self.stdout.write('\n5. Testing with non-existent player:')
        result = get_player_score("Non Existent Player")
        if result['success']:
            self.stdout.write(f"   Score: {result['score']}")
        else:
            self.stdout.write(f"   Expected error: {result['error']}")
        
        self.stdout.write(self.style.SUCCESS('\nTesting completed!'))