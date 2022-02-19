from django.db import models
from django.urls import reverse


class Device(models.Model):
    device_id = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    water_level = models.IntegerField(default=2000)
    moisture_level = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:device-info", kwargs={"id": self.id})
