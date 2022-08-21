from django.db import models
from base_model import BaseModel


class Venue(BaseModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    # housekeeping - automatically sets to last saved date time
    last_updated = models.DateTimeField(auto_now=True)
