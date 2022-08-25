from django.db import models


# This class only exists to remove a Pycharm warning that is fixed in the pro version django integration
class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True
