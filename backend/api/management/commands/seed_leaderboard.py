from django.core.management.base import BaseCommand
from api.models import LeaderboardEntry
import random

class Command(BaseCommand):
    help = 'Seed the database with sample leaderboard data'

    def handle(self, *args, **options):
        # Clear existing data
        LeaderboardEntry.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared existing leaderboard data'))

        # Sample names and their scores
        sample_data = [
            ('Alice Johnson', random.randint(1800, 2500)),
            ('Bob Smith', random.randint(1700, 2400)),
            ('Charlie Brown', random.randint(1600, 2300)),
            ('Diana Prince', random.randint(1500, 2200)),
            ('Eve Wilson', random.randint(1400, 2100)),
            ('Frank Miller', random.randint(1300, 2000)),
            ('Grace Lee', random.randint(1200, 1900)),
            ('Henry Davis', random.randint(1100, 1800)),
            ('Ivy Chen', random.randint(1000, 1700)),
            ('Jack Thompson', random.randint(900, 1600)),
            ('Kate Rodriguez', random.randint(800, 1500)),
            ('Liam O\'Connor', random.randint(700, 1400)),
            ('Maya Patel', random.randint(600, 1300)),
            ('Noah Kim', random.randint(500, 1200)),
            ('Olivia Martinez', random.randint(400, 1100)),
            ('Peter Anderson', random.randint(300, 1000)),
            ('Quinn Taylor', random.randint(200, 900)),
            ('Ruby Jackson', random.randint(100, 800)),
            ('Sam White', random.randint(50, 700)),
            ('Tina Garcia', random.randint(25, 600)),
        ]

        # Create leaderboard entries
        entries = []
        for name, score in sample_data:
            entry = LeaderboardEntry(name=name, score=score)
            entries.append(entry)

        # Bulk create for efficiency
        LeaderboardEntry.objects.bulk_create(entries)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {len(entries)} leaderboard entries')
        )

        # Display top 10 for verification
        top_entries = LeaderboardEntry.objects.all()[:10]
        self.stdout.write('\nTop 10 entries:')
        for i, entry in enumerate(top_entries, 1):
            self.stdout.write(f'{i}. {entry.name} - {entry.score}')