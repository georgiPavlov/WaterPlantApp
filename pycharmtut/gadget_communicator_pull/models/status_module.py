import uuid

from django.db import models
from django.urls import reverse


class Status(models.Model):
    execution_status = models.BooleanField(default=False)
    message = models.CharField(max_length=120)
    status_id = models.UUIDField(default=uuid.uuid4, editable=False)
    status_time = models.CharField(max_length=40, default="")

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:water-status", kwargs={"id": self.id})