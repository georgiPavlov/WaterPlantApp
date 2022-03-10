from rest_framework import serializers

from gadget_communicator_pull.models import Status


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['status_id', 'execution_status', 'message']

    def create(self, validated_data):
        validated_data = self.validated_data
        status_t = Status.objects.create(**validated_data)
        return status_t
