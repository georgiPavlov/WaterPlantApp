from django.db import models
from django.urls import reverse
from .device_module import Device


class MoisturePlan(models.Model):
    device_relation = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    plan_type = models.CharField(max_length=20)
    water_volume = models.IntegerField(default=0)
    moisture_threshold = models.IntegerField(default=0)
    check_interval = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:moisture-plan", kwargs={"id": self.id})
