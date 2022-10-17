from rest_framework import serializers
from gadget_communicator_pull.models.health_check import HealthCheck


class HealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheck
        fields = ['status_id', 'execution_status', 'message', 'status_time']

    def create(self, validated_data):
        validated_data = self.validated_data
        status_t = HealthCheck.objects.create(**validated_data)
        return status_t
