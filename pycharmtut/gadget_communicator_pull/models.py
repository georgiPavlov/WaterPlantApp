from typing import List
from django.db import models
from django.urls import reverse


class Device(models.Model):
    device_id = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    water_level = models.IntegerField(default=2000)
    moisture_level = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:device-info", kwargs={"id": self.id})


class BasicPlan(models.Model):
    device_relation = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    plan_type = models.CharField(max_length=20)
    water_volume = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:basic-plan", kwargs={"id": self.id})


class TimePlan(models.Model):
    basic_plan = models.OneToOneField(BasicPlan, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:time-plan", kwargs={"id": self.id})


class WaterTime(models.Model):
    time_plan_relation = models.ForeignKey(TimePlan, on_delete=models.CASCADE)
    weekday = models.CharField(max_length=20)
    time_water = models.TimeField()

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:device-info", kwargs={"id": self.id})


class MoisturePlan(models.Model):
    basic_plan = models.OneToOneField(BasicPlan, on_delete=models.CASCADE)
    moisture_threshold = models.IntegerField(default=0)
    check_interval = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:moisture-plan", kwargs={"id": self.id})


class Status(models.Model):
    watering_status = models.BooleanField(default=False)
    message = models.CharField(max_length=120)

    def get_absolute_url(self):
        return reverse("gadget_communicator_pull:water-status", kwargs={"id": self.id})
