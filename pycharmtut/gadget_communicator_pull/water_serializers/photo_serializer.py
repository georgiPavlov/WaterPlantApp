from rest_framework import serializers

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule


class DeviceSerializerForId(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_id']


class PhotoSerializer(serializers.ModelSerializer):
    devices = DeviceSerializerForId(many=True, read_only=True, source='photos')

    class Meta:
        model = PhotoModule
        fields = ['photo_id', 'photo_status', 'devices']
