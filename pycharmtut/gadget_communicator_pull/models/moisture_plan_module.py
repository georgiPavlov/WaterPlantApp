from django.db import models
from django.urls import reverse


class MoisturePlan(models.Model):
    name = models.CharField(max_length=20)
    plan_type = models.CharField(max_length=20)
    water_volume = models.IntegerField(default=0)
    moisture_threshold = models.IntegerField(default=0)
    check_interval = models.IntegerField(default=0)
    is_running = models.BooleanField(default=False)
    has_been_executed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:moisture-plan", kwargs={"id": self.id})
