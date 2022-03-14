from rest_framework import serializers

from gadget_communicator_pull.models.photo_module import PhotoModule


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoModule
        fields = ['photo_id', 'photo_status']
