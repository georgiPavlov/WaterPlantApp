from rest_framework import serializers

from gadget_communicator_pull.models import MoisturePlan
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class MoisturePlanSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True, source='devices_b')

    class Meta:
        model = MoisturePlan
        fields = ['name', 'plan_type', 'water_volume', 'device', 'moisture_threshold']

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
