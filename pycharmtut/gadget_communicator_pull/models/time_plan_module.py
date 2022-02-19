from django.db import models
from django.urls import reverse
from .device_module import Device
from .water_time_module import WaterTime


class TimePlan(models.Model):
    device_relation = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    plan_type = models.CharField(max_length=20)
    water_volume = models.IntegerField(default=0)
    water_time_relation = models.ManyToManyField(WaterTime)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:time-plan", kwargs={"id": self.id})