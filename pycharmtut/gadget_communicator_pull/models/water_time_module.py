from django.db import models
from django.urls import reverse
from gadget_communicator_pull.helper import WEEKDAYS
from gadget_communicator_pull.models import TimePlan


class WaterTime(models.Model):
    weekday = models.PositiveIntegerField(choices=WEEKDAYS)
    time_water = models.CharField(max_length=20)
    water_time_relation = models.ForeignKey(TimePlan, related_name='water_times', on_delete=models.CASCADE, null=True)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:water-info", kwargs={"id": self.id})
