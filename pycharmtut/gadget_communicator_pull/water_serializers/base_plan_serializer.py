from rest_framework import serializers
from gadget_communicator_pull.models.basic_plan_module import BasicPlan
from gadget_communicator_pull.models.device_module import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_id', 'label', 'water_level', 'moisture_level']


class BasePlanSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, read_only=True)

    class Meta:
        model = BasicPlan
        fields = ['name', 'plan_type', 'water_volume', 'devices']

    def create(self, validated_data):
        print("s")
        devices_data = validated_data.pop('devices')
        base_plan = BasicPlan.objects.create(**validated_data)
        for device_data in devices_data:
            print(device_data.device_id)
            print("ss")
            Device.objects.create(album=base_plan, **device_data)
        return base_plan
