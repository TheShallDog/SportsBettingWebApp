from django.db import models

# Create your models here.


# This class only exists to remove a Pycharm warning that is fixed in the pro version django integration
class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


# this class only exists as a leftover from a tutorial I was doing to learn django
class Course(BaseModel):
    image = models.ImageField(upload_to='images/')
    summary = models.TextField()

    def __str__(self):
        return self.summary


class MlbGame(BaseModel):
    game_id = models.IntegerField(primary_key=True)
    away_team = models.ForeignKey('MlbTeam', on_delete=models.CASCADE,
                                  related_name='away_team', blank=True, null=True)
    away_probable_pitcher = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE,
                                              related_name='away_probable_pitcher', blank=True, null=True)
    home_team = models.ForeignKey('MlbTeam', on_delete=models.CASCADE,
                                  related_name='home_team', blank=True, null=True)
    home_probable_pitcher = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE,
                                              related_name='home_probable_pitcher', blank=True, null=True)
    game_date = models.DateField(blank=True, null=True)
    game_type = models.CharField(max_length=10, blank=True, null=True)
    location = models.ForeignKey('MlbLocation', on_delete=models.CASCADE,
                                 blank=True, null=True)
    games_in_series_current = models.IntegerField(blank=True, null=True)
    games_in_series_total = models.IntegerField(blank=True, null=True)
    season = models.CharField(max_length=10, blank=True, null=True)


class MlbPlayer(BaseModel):
    player_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=40, blank=True, null=True)
    middle_name = models.CharField(max_length=40, blank=True, null=True)
    last_name = models.CharField(max_length=40, blank=True, null=True)
    name_title = models.CharField(max_length=40, blank=True, null=True)
    full_name = models.TextField(blank=True, null=True)
    position_name = models.CharField(max_length=20, blank=True, null=True)
    position_type = models.CharField(max_length=20, blank=True, null=True)
    position_abbreviation = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    current_team = models.ForeignKey('MlbTeam', on_delete=models.CASCADE, default=None,
                                     related_name='players_current_team', blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)


class MlbLocation(BaseModel):
    location_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)


class MlbTeam(BaseModel):
    team_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    abbreviation = models.CharField(max_length=5, blank=True, null=True)
    short_name = models.CharField(max_length=20, blank=True, null=True)
    team_code = models.CharField(max_length=5, blank=True, null=True)
    file_code = models.CharField(max_length=5, blank=True, null=True)
    franchise_name = models.CharField(max_length=20, blank=True, null=True)
    club_name = models.CharField(max_length=20, blank=True, null=True)
    league = models.CharField(max_length=50, blank=True, null=True)
    division = models.CharField(max_length=50, blank=True, null=True)
    home_venue = models.ForeignKey('MlbLocation', on_delete=models.CASCADE, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)


class MlbAtBat(BaseModel):
    game = models.ForeignKey('MlbGame', on_delete=models.CASCADE, blank=True, null=True)
    at_bat = models.IntegerField(blank=True, null=True)
    inning = models.IntegerField(blank=True, null=True)
    inning_half = models.CharField(max_length=15, blank=True, null=True)
    event_type = models.CharField(max_length=40, blank=True, null=True)
    pitching_team = models.ForeignKey('MlbTeam', on_delete=models.CASCADE,
                                      related_name='pitching_team', blank=True, null=True)
    pitcher = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE,
                                related_name='pitcher', blank=True, null=True)
    pitcher_hand = models.CharField(max_length=15, blank=True, null=True)
    batting_team = models.ForeignKey('MlbTeam', on_delete=models.CASCADE,
                                     related_name='batting_team', blank=True, null=True)
    batter = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE,
                               related_name='batter', blank=True, null=True)
    batter_hand = models.CharField(max_length=15, blank=True, null=True)
    lineup_position = models.IntegerField(blank=True, null=True)
    single = models.BooleanField(blank=True, null=True)
    double = models.BooleanField(blank=True, null=True)
    triple = models.BooleanField(blank=True, null=True)
    home_run = models.BooleanField(blank=True, null=True)
    scoring_play = models.BooleanField(blank=True, null=True)
    scoring_player_1 = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE, related_name='scorer_1',
                                         blank=True, null=True)
    scoring_player_2 = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE, related_name='scorer_2',
                                         blank=True, null=True)
    scoring_player_3 = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE, related_name='scorer_3',
                                         blank=True, null=True)
    scoring_player_4 = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE, related_name='scorer_4',
                                         blank=True, null=True)
    rbi = models.IntegerField(blank=True, null=True)
    earned_runs = models.IntegerField(blank=True, null=True)
    strikeout = models.BooleanField(blank=True, null=True)
    stolen_bases = models.IntegerField(blank=True, null=True)
    base_stealer_1 = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE, related_name='stealer_1',
                                       blank=True, null=True)
    base_stealer_2 = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE, related_name='stealer_2',
                                       blank=True, null=True)
    base_stealer_3 = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE, related_name='stealer_3',
                                       blank=True, null=True)
    error = models.BooleanField(blank=True, null=True)
    error_committer = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE, related_name='error_committer',
                                        blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class MlbUpcomingGames(BaseModel):
    game_id = models.IntegerField(primary_key=True)
    away_team = models.ForeignKey('MlbTeam', on_delete=models.CASCADE,
                                  related_name='upcoming_away_team', blank=True, null=True)
    away_probable_pitcher = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE,
                                              related_name='upcoming_away_probable_pitcher', blank=True, null=True)
    home_team = models.ForeignKey('MlbTeam', on_delete=models.CASCADE,
                                  related_name='upcoming_home_team', blank=True, null=True)
    home_probable_pitcher = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE,
                                              related_name='upcoming_home_probable_pitcher', blank=True, null=True)
    game_date_time = models.DateTimeField(blank=True, null=True)
    game_type = models.CharField(max_length=10, blank=True, null=True)
    location = models.ForeignKey('MlbLocation', on_delete=models.CASCADE,
                                 related_name='upcoming_location', blank=True, null=True)
    games_in_series_current = models.IntegerField(blank=True, null=True)
    games_in_series_total = models.IntegerField(blank=True, null=True)


class MlbUpcomingPlayers(BaseModel):
    game = models.ForeignKey('MlbUpcomingGames', on_delete=models.CASCADE, blank=True, null=True)
    team = models.ForeignKey('MlbTeam', on_delete=models.CASCADE,
                             related_name='upcoming_players_team', blank=True, null=True)
    player = models.ForeignKey('MlbPlayer', on_delete=models.CASCADE,
                               related_name='upcoming_player', blank=True, null=True)
    position_type = models.TextField(blank=True, null=True)
    home_or_away = models.TextField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)


class MlbPlayerSimulations(BaseModel):
    player_id = models.IntegerField(blank=True, null=True)
    player_name = models.TextField(blank=True, null=True)
    game_id = models.IntegerField(blank=True, null=True)
    game_date = models.DateField(blank=True, null=True)
    statistic = models.TextField(blank=True, null=True)
    time_frame = models.IntegerField(blank=True, null=True)

    stat_filters = models.TextField(blank=True, null=True)
    # this is a list of previous values pickled
    prev_values = models.BinaryField(blank=True, null=True)
    prev_avg = models.FloatField(blank=True, null=True)
    prev_st_dev = models.FloatField(blank=True, null=True)

    # this is the list of generated values pickled
    sim_values = models.BinaryField()
    # the following average and st_dev should match the previous and is just a check
    sim_avg = models.FloatField()
    sim_st_dev = models.FloatField()

    # actual value of stat from player, game, and filters
    actual_value = models.IntegerField(blank=True, null=True)


class MlbBovadaUpcomingPitchers(BaseModel):
    player_id = models.IntegerField(blank=True, null=True)
    player_name = models.TextField(blank=True, null=True)
    game_id = models.IntegerField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
    home_or_away = models.TextField(blank=True, null=True)
    stat = models.TextField(blank=True, null=True)
    over_line = models.FloatField(blank=True, null=True)
    under_line = models.FloatField(blank=True, null=True)
    over_odds = models.IntegerField(blank=True, null=True)
    under_odds = models.IntegerField(blank=True, null=True)


class MlbBovadaUpcomingBatters(BaseModel):
    player_id = models.IntegerField(blank=True, null=True)
    player_name = models.TextField(blank=True, null=True)
    game_id = models.IntegerField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
    home_or_away = models.TextField(blank=True, null=True)
    stat = models.TextField(blank=True, null=True)
    over_line = models.FloatField(blank=True, null=True)
    odds = models.IntegerField(blank=True, null=True)


class MlbBovadaPitchersPostSimData(BaseModel):
    player_id = models.IntegerField(blank=True, null=True)
    player_name = models.TextField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
    stat = models.TextField(blank=True, null=True)
    stat_filter = models.TextField(blank=True, null=True)
    time_interval = models.IntegerField(blank=True, null=True)
    sim_option = models.TextField(blank=True, null=True)
    round_option = models.TextField(blank=True, null=True)
    bet_option = models.TextField(blank=True, null=True)
    bet_line = models.FloatField(blank=True, null=True)
    bet_odds = models.IntegerField(blank=True, null=True)
    expected_prob_avg = models.FloatField(blank=True, null=True)
    actual_result_avg = models.FloatField(blank=True, null=True)
    difference = models.FloatField(blank=True, null=True)


class MlbBovadaPitchersBetComparison(BaseModel):
    player_id = models.IntegerField(blank=True, null=True)
    player_name = models.TextField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
    upcoming_game_id = models.IntegerField(blank=True, null=True)
    stat = models.TextField(blank=True, null=True)
    bet_option = models.TextField(blank=True, null=True)
    bovada_bet_line = models.FloatField(blank=True, null=True)
    bovada_bet_odds = models.IntegerField(blank=True, null=True)
    bovada_implied_probability = models.FloatField(blank=True, null=True)
    sim_bet_odds = models.IntegerField(blank=True, null=True)
    sim_implied_probability = models.FloatField(blank=True, null=True)
    expected_value_per_unit = models.FloatField(blank=True, null=True)
    bet_rating = models.TextField(blank=True, null=True)
