# Generated by Django 4.0.5 on 2022-08-15 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlb', '0013_rename_player_mlbplayersimulations_player_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlbbovadapitchersbetcomparison',
            name='bet_rating',
            field=models.TextField(blank=True, null=True),
        ),
    ]
