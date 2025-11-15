from django.core.management.base import BaseCommand
from api.models import Problem


class Command(BaseCommand):
    help = "Delete all Problem records (cascades to related submissions and test cases)."

    def handle(self, *args, **options):
        count = Problem.objects.count()
        deleted_count, details = Problem.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            f"Deleted {count} problems (rows affected including cascades: {deleted_count})."
        ))
        for model, num in details.items():
            model_name = getattr(model, "__name__", None)
            if not model_name:
                # Django may return app_label.ModelName strings in some contexts
                model_name = str(model)
            self.stdout.write(f" - {model_name}: {num}")
