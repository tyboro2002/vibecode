from django.core.management.base import BaseCommand
from django.core import serializers
from api.models import TestCase
import json


class Command(BaseCommand):
    help = "Export all test cases to a JSON fixture file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default="testcases_fixture.json",
            help="Output filename for the fixture (default: testcases_fixture.json)",
        )
        parser.add_argument(
            "--problem",
            "-p",
            type=str,
            default=None,
            help="Export test cases for a specific problem name only",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        problem_name = options["problem"]
        
        # Filter test cases
        if problem_name:
            testcases = TestCase.objects.filter(problem__name=problem_name)
        else:
            testcases = TestCase.objects.all()
        
        count = testcases.count()
        
        if count == 0:
            if problem_name:
                self.stdout.write(self.style.WARNING(
                    f"No test cases found for problem '{problem_name}'."
                ))
            else:
                self.stdout.write(self.style.WARNING("No test cases found to export."))
            return
        
        # Serialize to JSON
        data = serializers.serialize("json", testcases, indent=2)
        
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(data)
        
        if problem_name:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully exported {count} test cases for '{problem_name}' to '{output_file}'"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully exported {count} test cases to '{output_file}'"
            ))
        self.stdout.write(f"To load this fixture later, run:")
        self.stdout.write(f"  python manage.py loaddata {output_file}")
