from django.db import models


class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    date_time = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)

    # status codes
    abstract_game_state = models.CharField(max_length=100, blank=True, null=True)
    abstract_game_code = models.CharField(max_length=10, blank=True, null=True)
    coded_game_state = models.CharField(max_length=10, blank=True, null=True)
    detailed_state = models.CharField(max_length=100, blank=True, null=True)
    status_code = models.CharField(max_length=10, blank=True, null=True)

    # team information
    away_team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='away_team',
                                  blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)             # only in JSON after complete game
    away_is_winner = models.BooleanField(blank=True, null=True)         # only in JSON after complete game

    home_team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='home_team',
                                  blank=True, null=True)
    home_score = models.IntegerField(blank=True, null=True)             # only in JSON after complete game
    home_is_winner = models.BooleanField(blank=True, null=True)         # only in JSON after complete game

    # location information
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='game_venue',
                              blank=True, null=True)

    # general game info
    double_header = models.CharField(max_length=10, blank=True, null=True)
    day_night = models.CharField(max_length=100, blank=True, null=True)
    total_games_in_series = models.IntegerField(blank=True, null=True)
    current_game_in_series = models.IntegerField(blank=True, null=True)
    series_description = models.CharField(max_length=100, blank=True, null=True)
    season = models.CharField(max_length=10, blank=True, null=True)

    # housekeeping - automatically sets to last saved date time
    last_updated = models.DateTimeField(auto_now=True)
