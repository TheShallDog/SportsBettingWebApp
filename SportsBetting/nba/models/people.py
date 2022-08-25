from django.db import models
from ..models import BaseModel
import requests
import time
import datetime
from .team import Team


class People(BaseModel):
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

    @staticmethod
    def populate():
        try:
            teams = Team.objects.filter(active=True)
        except:
            print("need to populate team table first")
            return

        for team in teams:
            url = f"https://statsapi.mlb.com/api/v1/teams/{team.id}/roster"
            print(url)
            time.sleep(.1)
            response = requests.get(url)
            jason = response.json()
            roster = jason['roster']
            for person_id in roster:
                People.update(person_id)
                obj = People.objects.get(id=person_id)
                obj.current_team = team
                obj.save()

    @staticmethod
    def update(person_id, override=False):
        if People.objects.get(id=person_id).exists():
            if People.objects.get(id=person_id).last_updated > (datetime.date.today() - datetime.timedelta(weeks=1)):
                if override is not True:
                    return

        person_id_json = People.get_json(person_id)
        p = person_id_json['people'][0]

        full_name = p['fullName']
        first_name = p['firstName']

        try:
            middle_name = p['middleName']
        except KeyError:
            middle_name = None

        last_name = p['lastName']

        try:
            name_title = p['nameTitle']
        except KeyError:
            name_title = None

        position_code = p['primaryPosition']['code']
        position_name = p['primaryPosition']['name']
        position_type = p['primaryPosition']['type']
        position_abbreviation = p['primaryPosition']['abbreviation']

        bat_side_code = p['batSide']['code']
        bat_side_description = p['batSide']['description']
        pitch_hand_code = p['pitchHand']['code']
        pitch_hand_description = p['pitchHand']['description']

        strike_zone_top = p['strikeZoneTop']
        strike_zone_bottom = p['strikeZoneBottom']

        is_player = p['isPlayer']
        current_age = p['currentAge']
        active = bool(p['active'])
        link = p['link']
        current_team = None

        obj, created = People.objects.update_or_create(
            id=person_id,
            defaults={'full_name': full_name,
                      'first_name': first_name,
                      'middle_name': middle_name,
                      'last_name': last_name,
                      'name_title': name_title,
                      'position_code': position_code,
                      'position_name': position_name,
                      'position_type': position_type,
                      'position_abbreviation': position_abbreviation,
                      'bat_side_code': bat_side_code,
                      'bat_side_description': bat_side_description,
                      'pitch_hand_code': pitch_hand_code,
                      'pitch_hand_description': pitch_hand_description,
                      'strike_zone_top': strike_zone_top,
                      'strike_zone_bottom': strike_zone_bottom,
                      'is_player': is_player,
                      'current_age': current_age,
                      'active': active,
                      'link': link,
                      'current_team': current_team})
        obj.save()

    @staticmethod
    def get_json(person_id):
        url = f"https://statsapi.mlb.com/api/v1/people/{person_id}"
        print(url)
        time.sleep(.1)
        response = requests.get(url)
        return response.json()
