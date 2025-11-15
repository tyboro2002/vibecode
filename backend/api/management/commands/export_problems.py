from django.core.management.base import BaseCommand
from django.core import serializers
from api.models import Problem
import json


class Command(BaseCommand):
    help = "Export all problems to a JSON fixture file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default="problems_fixture.json",
            help="Output filename for the fixture (default: problems_fixture.json)",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        
        problems = Problem.objects.all()
        count = problems.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING("No problems found to export."))
            return
        
        # Serialize to JSON
        data = serializers.serialize("json", problems, indent=2)
        
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(data)
        
        self.stdout.write(self.style.SUCCESS(
            f"Successfully exported {count} problems to '{output_file}'"
        ))
        self.stdout.write(f"To load this fixture later, run:")
        self.stdout.write(f"  python manage.py loaddata {output_file}")
