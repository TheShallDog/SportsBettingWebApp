# Generated by Django 4.0.5 on 2022-08-15 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlb', '0014_mlbbovadapitchersbetcomparison_bet_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mlbplayersimulations',
            name='game_date',
        ),
    ]
