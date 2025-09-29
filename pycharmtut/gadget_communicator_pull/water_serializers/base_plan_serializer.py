from rest_framework import serializers
from gadget_communicator_pull.models.basic_plan_module import BasicPlan
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class BasePlanSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, read_only=True, source='devices_b')

    class Meta:
        model = BasicPlan
        fields = ['name', 'plan_type', 'water_volume', 'devices', 'has_been_executed']

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













