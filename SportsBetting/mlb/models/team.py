from django.db import models
from base_model import BaseModel


class Team(BaseModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    # different team references
    team_code = models.CharField(max_length=100, blank=True, null=True)
    file_code = models.CharField(max_length=100, blank=True, null=True)
    abbreviation = models.CharField(max_length=100, blank=True, null=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=100, blank=True, null=True)
    franchise_name = models.CharField(max_length=100, blank=True, null=True)
    club_name = models.CharField(max_length=100, blank=True, null=True)
    location_name = models.CharField(max_length=100, blank=True, null=True)

    # general team info
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='home_venue',
                              blank=True, null=True)
    league_name = models.CharField(max_length=100, blank=True, null=True)
    division_name = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    # housekeeping - automatically sets to last saved date time
    last_updated = models.DateTimeField(auto_now=True)
