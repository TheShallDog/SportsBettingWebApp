from django.db import models
from base_model import BaseModel
import time
import requests
import datetime


class Venue(BaseModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    # housekeeping - automatically sets to last saved date time
    last_updated = models.DateTimeField(auto_now=True)

    @staticmethod
    def update(venue_id, override=False):
        if Venue.objects.get(id=venue_id).exists():
            if Venue.objects.get(id=venue_id).last_updated > (datetime.date.today() - datetime.timedelta(weeks=1)):
                if override is not True:
                    return

        venue_id_json = Venue.get_json(venue_id)
        v = venue_id_json['venues'][0]

        name = v['name']
        active = bool(v['active'])
        link = v['link']

        obj, created = Venue.objects.update_or_create(
            id=venue_id,
            defaults={'name': name,
                      'active': active,
                      'link': link})
        obj.save()

    @staticmethod
    def get_json(location_id):
        url = f"https://statsapi.mlb.com/api/v1/venues/{location_id}"
        print(url)
        time.sleep(.1)
        response = requests.get(url)
        return response.json()
