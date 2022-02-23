from gadget_communicator_pull.models import WaterTime, TimePlan
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer
from rest_framework import serializers


class WaterTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterTime
        fields = ['time_water', 'weekday']


class TimePlanSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True, source='devices_b')
    weekday_times = WaterTimeSerializer(many=True,read_only=True, source='devices_b')

    class Meta:
        model = TimePlan
        fields = ['name', 'plan_type', 'water_volume', 'device', 'times']

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
