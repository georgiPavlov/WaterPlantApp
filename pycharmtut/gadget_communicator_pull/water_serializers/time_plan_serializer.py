from gadget_communicator_pull.helpers.helper import WEEKDAYS
from gadget_communicator_pull.models import WaterTime, TimePlan
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer
from rest_framework import serializers


class WaterTimeSerializer(serializers.ModelSerializer):
    weekday = serializers.SerializerMethodField()

    def get_weekday(self, water_time):
        return WEEKDAYS.get_selected_values(water_time.weekday).pop()

    class Meta:
        model = WaterTime
        fields = ['time_water', 'weekday']


class TimePlanSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, read_only=True, source='devices_t')
    weekday_times = WaterTimeSerializer(many=True, read_only=True, source='water_times')

    class Meta:
        model = TimePlan
        fields = ['name', 'plan_type', 'water_volume', 'has_been_executed', 'devices', 'weekday_times']

    # def create(self, validated_data):
    # print("s")
    # devices_data = validated_data.pop('devices_b')
    # base_plan = BasicPlan.objects.create(**validated_data)
    # for device_data in devices_data:
    #     print(device_data.device_id)
    #     print("ss")
    #     Device.objects.create(album=base_plan, **device_data)
    # return base_plan
    # devices_data = validated_data.pop('devices_b')
    # base_plan = BasicPlan.objects.create(**validated_data)
    #
    # for device_data in devices_data:
    #     BasicPlan.objects.create(devices_b=base_plan, **device_data)
