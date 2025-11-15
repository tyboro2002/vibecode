from django.core.management.base import BaseCommand
from api.models import Problem


class Command(BaseCommand):
    help = "Add problems from hardcoded list (does not clear existing)."

    def handle(self, *args, **options):
        try:
            # Import inside handle so edits to the file are picked up without restart
            from api.management.problems_data import PROBLEMS  # type: ignore
        except Exception:
            self.stderr.write(self.style.ERROR(
                "Failed to import PROBLEMS from api.management.problems_data"
            ))
            raise

        if not isinstance(PROBLEMS, list) or not PROBLEMS:
            self.stdout.write(self.style.WARNING("No problems to add (PROBLEMS is empty)."))
            return

        instances = []
        for i, item in enumerate(PROBLEMS, start=1):
            name = (item.get("name") or "").strip()
            points = item.get("points")
            assignment = item.get("assignment") or ""

            if not name or not isinstance(points, int):
                self.stderr.write(self.style.WARNING(
                    f"Skipping item #{i}: invalid name/points"
                ))
                continue

            instances.append(Problem(name=name, points=points, assignment=assignment))

        if not instances:
            self.stdout.write(self.style.WARNING("No valid problems to create."))
            return

        Problem.objects.bulk_create(instances)
        self.stdout.write(self.style.SUCCESS(f"Added {len(instances)} problems."))
