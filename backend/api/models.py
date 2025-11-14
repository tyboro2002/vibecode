from django.db import models

class LeaderboardEntry(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField()
    zauth_id = models.IntegerField(null=True, blank=True)  # Zeus user ID
    picture_url = models.URLField(max_length=500, null=True, blank=True)  # Profile picture URL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-score', 'created_at']  # Order by score descending, then by creation time
        verbose_name = "Leaderboard Entry"
        verbose_name_plural = "Leaderboard Entries"

    def __str__(self):
        return f"{self.name} - {self.score}"


class Problem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    points = models.IntegerField()
    assignment = models.TextField()


class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    submission_time = models.DateTimeField(auto_now_add=True)
    submission_correct = models.BooleanField(default=False)
    submisser = models.ForeignKey(LeaderboardEntry, on_delete=models.CASCADE)


class TestCase(models.Model):
    id = models.AutoField(primary_key=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
