# Generated by Django 4.0.5 on 2022-08-12 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlb', '0005_remove_mlbplayersimulations_game_date_unix'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlbplayersimulations',
            name='game_date_unix',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
