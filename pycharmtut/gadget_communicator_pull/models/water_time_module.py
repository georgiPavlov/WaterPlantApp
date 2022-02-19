from django.db import models
from django.urls import reverse
from gadget_communicator_pull.helper import WEEKDAYS


class WaterTime(models.Model):
    weekday = models.PositiveIntegerField(choices=WEEKDAYS)
    time_water = models.CharField(max_length=20)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:water-info", kwargs={"id": self.id})
