# Generated by Django 4.0.5 on 2022-08-12 01:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
                ('summary', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbBovadaUpcomingBatters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_id', models.IntegerField(blank=True, null=True)),
                ('player_name', models.TextField(blank=True, null=True)),
                ('home_or_away', models.TextField(blank=True, null=True)),
                ('stat', models.TextField(blank=True, null=True)),
                ('over_line', models.FloatField(blank=True, null=True)),
                ('odds', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbBovadaUpcomingPitchers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_id', models.IntegerField(blank=True, null=True)),
                ('player_name', models.TextField(blank=True, null=True)),
                ('home_or_away', models.TextField(blank=True, null=True)),
                ('stat', models.TextField(blank=True, null=True)),
                ('over_line', models.FloatField(blank=True, null=True)),
                ('under_line', models.FloatField(blank=True, null=True)),
                ('over_odds', models.IntegerField(blank=True, null=True)),
                ('under_odds', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbLocation',
            fields=[
                ('location_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('active', models.BooleanField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbPlayer',
            fields=[
                ('player_id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=40, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=40, null=True)),
                ('last_name', models.CharField(blank=True, max_length=40, null=True)),
                ('name_title', models.CharField(blank=True, max_length=40, null=True)),
                ('full_name', models.TextField(blank=True, null=True)),
                ('position_name', models.CharField(blank=True, max_length=20, null=True)),
                ('position_type', models.CharField(blank=True, max_length=20, null=True)),
                ('position_abbreviation', models.CharField(blank=True, max_length=20, null=True)),
                ('active', models.BooleanField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbPlayerSimulations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player', models.IntegerField(blank=True, null=True)),
                ('game_id', models.IntegerField(blank=True, null=True)),
                ('game_date', models.FloatField(blank=True, null=True)),
                ('statistic', models.TextField(blank=True, null=True)),
                ('time_frame', models.IntegerField(blank=True, null=True)),
                ('stat_filters', models.TextField(blank=True, null=True)),
                ('prev_values', models.BinaryField(blank=True, null=True)),
                ('prev_avg', models.FloatField(blank=True, null=True)),
                ('prev_st_dev', models.FloatField(blank=True, null=True)),
                ('sim_values', models.BinaryField()),
                ('sim_avg', models.FloatField()),
                ('sim_st_dev', models.FloatField()),
                ('actual_value', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbTeam',
            fields=[
                ('team_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('abbreviation', models.CharField(blank=True, max_length=5, null=True)),
                ('short_name', models.CharField(blank=True, max_length=20, null=True)),
                ('team_code', models.CharField(blank=True, max_length=5, null=True)),
                ('file_code', models.CharField(blank=True, max_length=5, null=True)),
                ('franchise_name', models.CharField(blank=True, max_length=20, null=True)),
                ('club_name', models.CharField(blank=True, max_length=20, null=True)),
                ('league', models.CharField(blank=True, max_length=50, null=True)),
                ('division', models.CharField(blank=True, max_length=50, null=True)),
                ('active', models.BooleanField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
                ('home_venue', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mlb.mlblocation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbUpcomingGames',
            fields=[
                ('game_id', models.IntegerField(primary_key=True, serialize=False)),
                ('game_date_time', models.DateTimeField(blank=True, null=True)),
                ('game_type', models.CharField(blank=True, max_length=10, null=True)),
                ('games_in_series_current', models.IntegerField(blank=True, null=True)),
                ('games_in_series_total', models.IntegerField(blank=True, null=True)),
                ('away_probable_pitcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upcoming_away_probable_pitcher', to='mlb.mlbplayer')),
                ('away_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upcoming_away_team', to='mlb.mlbteam')),
                ('home_probable_pitcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upcoming_home_probable_pitcher', to='mlb.mlbplayer')),
                ('home_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upcoming_home_team', to='mlb.mlbteam')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upcoming_location', to='mlb.mlblocation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbUpcomingPlayers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_type', models.TextField(blank=True, null=True)),
                ('home_or_away', models.TextField(blank=True, null=True)),
                ('first_name', models.TextField(blank=True, null=True)),
                ('last_name', models.TextField(blank=True, null=True)),
                ('game', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mlb.mlbupcominggames')),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upcoming_player', to='mlb.mlbplayer')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upcoming_players_team', to='mlb.mlbteam')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='mlbplayer',
            name='current_team',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='players_current_team', to='mlb.mlbteam'),
        ),
        migrations.CreateModel(
            name='MlbGame',
            fields=[
                ('game_id', models.IntegerField(primary_key=True, serialize=False)),
                ('game_date', models.DateField(blank=True, null=True)),
                ('game_type', models.CharField(blank=True, max_length=10, null=True)),
                ('games_in_series_current', models.IntegerField(blank=True, null=True)),
                ('games_in_series_total', models.IntegerField(blank=True, null=True)),
                ('season', models.CharField(blank=True, max_length=10, null=True)),
                ('away_probable_pitcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='away_probable_pitcher', to='mlb.mlbplayer')),
                ('away_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='away_team', to='mlb.mlbteam')),
                ('home_probable_pitcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_probable_pitcher', to='mlb.mlbplayer')),
                ('home_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_team', to='mlb.mlbteam')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mlb.mlblocation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MlbAtBat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('at_bat', models.IntegerField(blank=True, null=True)),
                ('inning', models.IntegerField(blank=True, null=True)),
                ('inning_half', models.CharField(blank=True, max_length=15, null=True)),
                ('event_type', models.CharField(blank=True, max_length=40, null=True)),
                ('pitcher_hand', models.CharField(blank=True, max_length=15, null=True)),
                ('batter_hand', models.CharField(blank=True, max_length=15, null=True)),
                ('lineup_position', models.IntegerField(blank=True, null=True)),
                ('single', models.BooleanField(blank=True, null=True)),
                ('double', models.BooleanField(blank=True, null=True)),
                ('triple', models.BooleanField(blank=True, null=True)),
                ('home_run', models.BooleanField(blank=True, null=True)),
                ('scoring_play', models.BooleanField(blank=True, null=True)),
                ('rbi', models.IntegerField(blank=True, null=True)),
                ('earned_runs', models.IntegerField(blank=True, null=True)),
                ('strikeout', models.BooleanField(blank=True, null=True)),
                ('stolen_bases', models.IntegerField(blank=True, null=True)),
                ('error', models.BooleanField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('base_stealer_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stealer_1', to='mlb.mlbplayer')),
                ('base_stealer_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stealer_2', to='mlb.mlbplayer')),
                ('base_stealer_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stealer_3', to='mlb.mlbplayer')),
                ('batter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batter', to='mlb.mlbplayer')),
                ('batting_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batting_team', to='mlb.mlbteam')),
                ('error_committer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='error_committer', to='mlb.mlbplayer')),
                ('game', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mlb.mlbgame')),
                ('pitcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pitcher', to='mlb.mlbplayer')),
                ('pitching_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pitching_team', to='mlb.mlbteam')),
                ('scoring_player_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scorer_1', to='mlb.mlbplayer')),
                ('scoring_player_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scorer_2', to='mlb.mlbplayer')),
                ('scoring_player_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scorer_3', to='mlb.mlbplayer')),
                ('scoring_player_4', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scorer_4', to='mlb.mlbplayer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
