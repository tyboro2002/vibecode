# Generated migration for adding zauth_id field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderboardentry',
            name='zauth_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
