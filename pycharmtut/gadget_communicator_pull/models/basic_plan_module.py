from django.db import models
from django.urls import reverse


class BasicPlan(models.Model):
    name = models.CharField(max_length=20, unique=True)
    plan_type = models.CharField(max_length=20)
    water_volume = models.IntegerField(default=0)
    has_been_executed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:basic-plan", kwargs={"id": self.id})
