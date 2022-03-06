from abc import ABC

from rest_framework import serializers

from gadget_communicator_pull.models import BasicPlan, TimePlan, MoisturePlan


class PlansSerializer(serializers.Serializer):
    basic = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    moisture = serializers.SerializerMethodField()

    def get_basic(self, devices):
        print("in_in")
        return BasicPlan.objects.filter(devices_b__in=self.devices)

    def get_time(self, devices):
        return TimePlan.objects.filter(devices_t__in=self.devices)

    def get_moisture(self, devices):
        return MoisturePlan.objects.filter(devices_m__in=self.devices)

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        return instance
