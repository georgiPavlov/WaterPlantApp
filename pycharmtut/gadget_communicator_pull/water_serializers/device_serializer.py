from rest_framework import serializers
from gadget_communicator_pull.models.device_module import Device, WaterChart


class WaterChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterChart
        fields = ['water_chart']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_id', 'label', 'water_level', 'moisture_level', 'water_container_capacity', 'water_reset',
                  'send_email', 'is_connected']
