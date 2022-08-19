from django.db import models


class People(models.Model):
    id = models.IntegerField(primary_key=True)

    # complete name information
    full_name = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    name_title = models.CharField(max_length=100, blank=True, null=True)

    # position information
    position_code = models.IntegerField(blank=True, null=True)
    position_name = models.CharField(max_length=100, blank=True, null=True)
    position_type = models.CharField(max_length=100, blank=True, null=True)
    position_abbreviation = models.CharField(max_length=100, blank=True, null=True)

    # batting and pitching handing
    bat_side_code = models.CharField(max_length=10, blank=True, null=True)
    bat_side_description = models.CharField(max_length=100, blank=True, null=True)
    pitch_hand_code = models.CharField(max_length=10, blank=True, null=True)
    pitch_hand_description = models.CharField(max_length=100, blank=True, null=True)

    # strike_zone - could be used to determine pitcher batter matchup stats
    strike_zone_top = models.FloatField(blank=True, null=True)
    strike_zone_bottom = models.FloatField(blank=True, null=True)

    # general info
    is_player = models.BooleanField(blank=True, null=True)
    current_age = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)
    current_team = models.ForeignKey('Team', on_delete=models.CASCADE, default=None,
                                     related_name='persons_current_team',
                                     blank=True, null=True)

    # housekeeping - automatically sets to last saved date time
    last_updated = models.DateTimeField(auto_now=True)
