from rest_framework import serializers
from gadget_communicator_pull.models.device_module import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_id', 'label', 'water_level', 'moisture_level']
