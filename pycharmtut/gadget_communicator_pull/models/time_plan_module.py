from django.db import models
from django.urls import reverse


class TimePlan(models.Model):
    name = models.CharField(max_length=20)
    plan_type = models.CharField(max_length=20)
    water_volume = models.IntegerField(default=0)
    execute_only_once = models.BooleanField(default=False)
    is_running = models.BooleanField(default=False)
    has_been_executed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:time-plan", kwargs={"id": self.id})