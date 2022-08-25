from django.db import models
from ..models import BaseModel
from .venue import Venue
import datetime
import time
import requests


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

    @staticmethod
    def update(team_id, override=False):
        if Team.objects.get(id=team_id).exists():
            if Team.objects.get(id=team_id).last_updated > (datetime.date.today() - datetime.timedelta(weeks=1)):
                if override is not True:
                    return

        team_id_json = Team.get_json(team_id)
        t = team_id_json['teams'][0]

        name = t['name']

        team_code = t['teamCode']
        file_code = t['fileCode']
        abbreviation = t['abbreviation']
        team_name = t['teamName']
        short_name = t['shortName']
        franchise_name = t['franchiseName']
        club_name = t['clubName']
        location_name = t['locationName']

        temp_id = int(t['venue']['id'])
        Venue.update(temp_id)
        venue = Venue.objects.get(id=temp_id)

        league_name = t['league']['name']

        try:
            division_name = t['division']['name']
        except KeyError:
            division_name = None

        active = bool(t['active'])
        link = t['link']

        obj, created = Team.objects.update_or_create(
            id=team_id,
            defaults={'name': name,
                      'team_code': team_code,
                      'file_code': file_code,
                      'abbreviation': abbreviation,
                      'team_name': team_name,
                      'short_name': short_name,
                      'franchise_name': franchise_name,
                      'club_name': club_name,
                      'location_name': location_name,
                      'venue': venue,
                      'league_name': league_name,
                      'division_name': division_name,
                      'active': active,
                      'link': link})
        obj.save()

    @staticmethod
    def get_json(team_id):
        url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}"
        print(url)
        time.sleep(.1)
        response = requests.get(url)
        return response.json()
