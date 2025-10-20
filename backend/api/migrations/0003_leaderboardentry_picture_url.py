# Generated migration for adding picture_url field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_leaderboardentry_zauth_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderboardentry',
            name='picture_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
