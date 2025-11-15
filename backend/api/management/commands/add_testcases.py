from django.core.management.base import BaseCommand
from api.models import Problem, TestCase
from api.management.testcases_data import TESTCASES


class Command(BaseCommand):
    help = 'Add test cases for problems from hardcoded data'

    def handle(self, *args, **options):
        added_count = 0
        skipped_count = 0
        error_count = 0

        for problem_name, testcases in TESTCASES.items():
            try:
                # Find the problem by name
                problem = Problem.objects.filter(name=problem_name).first()
                
                if not problem:
                    self.stdout.write(
                        self.style.WARNING(f"Problem '{problem_name}' not found. Skipping test cases.")
                    )
                    skipped_count += len(testcases)
                    continue
                
                # Add each test case
                for testcase_data in testcases:
                    TestCase.objects.create(
                        problem=problem,
                        input_data=testcase_data['input_data'],
                        expected_output=testcase_data['expected_output'],
                        is_public=testcase_data.get('is_public', True)  # Default to public if not specified
                    )
                    added_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f"Added {len(testcases)} test case(s) for '{problem_name}'")
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error adding test cases for '{problem_name}': {str(e)}")
                )
                error_count += len(testcases)
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"✓ Successfully added: {added_count} test case(s)"))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"⊘ Skipped: {skipped_count} test case(s)"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"✗ Failed: {error_count} test case(s)"))
        self.stdout.write("="*50)
