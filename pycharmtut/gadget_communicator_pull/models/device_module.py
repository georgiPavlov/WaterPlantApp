from django.db import models
from django.urls import reverse
from gadget_communicator_pull.models.basic_plan_module import BasicPlan
from gadget_communicator_pull.models.time_plan_module import TimePlan
from gadget_communicator_pull.models.moisture_plan_module import MoisturePlan
from gadget_communicator_pull.models.status_module import Status


class Device(models.Model):
    device_relation_b = models.ManyToManyField(BasicPlan, related_name='devices_b')
    device_relation_t = models.ManyToManyField(TimePlan, related_name='devices_t')
    device_relation_m = models.ManyToManyField(MoisturePlan, related_name='devices_m')
    status_relation = models.ForeignKey(Status, related_name='statuses', on_delete=models.CASCADE, null=True)

    device_id = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    water_level = models.IntegerField(default=2000)
    moisture_level = models.IntegerField(default=0)


    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:device-info", kwargs={"id": self.id})

    class Meta:
        unique_together = ['device_id', 'label', "water_level", "water_level"]
        ordering = ['device_id']