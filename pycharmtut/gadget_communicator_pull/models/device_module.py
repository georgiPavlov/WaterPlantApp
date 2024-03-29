from django.db import models
from django.urls import reverse
from gadget_communicator_pull.models.basic_plan_module import BasicPlan
from gadget_communicator_pull.models.health_check import HealthCheck
from gadget_communicator_pull.models.photo_module import PhotoModule
from gadget_communicator_pull.models.time_plan_module import TimePlan
from gadget_communicator_pull.models.moisture_plan_module import MoisturePlan
from gadget_communicator_pull.models.status_module import Status


class Device(models.Model):
    owner = models.ForeignKey('auth.User', related_name='announces', on_delete=models.CASCADE, null=True)
    device_relation_b = models.ManyToManyField(BasicPlan, related_name='devices_b')
    device_relation_t = models.ManyToManyField(TimePlan, related_name='devices_t')
    device_relation_m = models.ManyToManyField(MoisturePlan, related_name='devices_m')
    status_relation = models.ManyToManyField(Status, related_name='statuses')
    health_relation = models.ManyToManyField(HealthCheck, related_name='health_check')
    photo_relation = models.ManyToManyField(PhotoModule, related_name='photos')

    device_id = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    water_level = models.IntegerField(default=100)
    moisture_level = models.IntegerField(default=0)
    water_container_capacity = models.IntegerField(default=2000)
    water_reset = models.BooleanField(default=False)
    send_email = models.BooleanField(default=False)
    is_connected = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:device-info", kwargs={"id": self.id})

    class Meta:
        unique_together = ['device_id', 'label']
        ordering = ['device_id']


class WaterChart(models.Model):
    water_chart = models.IntegerField(default=100)
    device_relation = models.ForeignKey(Device, related_name='water_charts', on_delete=models.CASCADE, null=True)
