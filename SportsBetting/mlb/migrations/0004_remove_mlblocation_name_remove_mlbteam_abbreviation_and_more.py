# Generated by Django 4.0.5 on 2022-07-24 03:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlb', '0003_mlbgame_away_probable_pitcher_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mlblocation',
            name='name',
        ),
        migrations.RemoveField(
            model_name='mlbteam',
            name='abbreviation',
        ),
        migrations.RemoveField(
            model_name='mlbteam',
            name='name',
        ),
    ]
