from django.core.management.base import BaseCommand
from api.models import TestCase


class Command(BaseCommand):
    help = 'Delete all test cases from the database'

    def handle(self, *args, **options):
        # Get count before deletion
        count = TestCase.objects.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING("No test cases found in the database."))
            return
        
        # Delete all test cases
        deletion_details = TestCase.objects.all().delete()
        
        # deletion_details is a tuple: (total_deleted, {model_name: count})
        total_deleted = deletion_details[0]
        details = deletion_details[1]
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"✓ Successfully deleted {total_deleted} object(s)"))
        self.stdout.write("\nDeletion breakdown:")
        
        for model, count in details.items():
            model_name = getattr(model, "__name__", None) or str(model)
            self.stdout.write(f"  - {model_name}: {count}")
        
        self.stdout.write("="*50)
