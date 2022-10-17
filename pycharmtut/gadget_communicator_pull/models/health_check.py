import uuid

from django.db import models
from django.urls import reverse


class HealthCheck(models.Model):
    execution_status = models.BooleanField(default=False)
    message = models.CharField(max_length=120)
    status_id = models.UUIDField(default=uuid.uuid4, editable=False)
    status_time = models.CharField(max_length=40, default="")

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:water-status", kwargs={"id": self.id})

    # def save(self):
    #     count = HealthCheck.objects.all().count()
    #     save_permission = HealthCheck.has_add_permission(self)
    #
    #     if count < 2:
    #         super(HealthCheck, self).save()
    #     elif save_permission:
    #         super(HealthCheck, self).save()
    #
    # def has_add_permission(self):
    #     return HealthCheck.objects.filter(status_id=self.status_id).exists()
