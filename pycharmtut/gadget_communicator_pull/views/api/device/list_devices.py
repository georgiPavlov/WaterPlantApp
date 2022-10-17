from django.http import JsonResponse
from rest_framework import generics, permissions
from gadget_communicator_pull.helpers import time_keeper

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class ApiListDevices(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        devices = Device.objects.filter(owner=request.user)
        connected_devices = devices.filter(is_connected=True)
        date_k = time_keeper.TimeKeeper(time_keeper.TimeKeeper.get_current_date())
        for connected_device in connected_devices:
            current_time_minus_delta = date_k.get_current_time_minus_delta_seconds(15)
            device_last_check = connected_device.health_relation.all().first()
            device_last_time_check = date_k.get_time_from_time_string(device_last_check.status_time)
            if device_last_time_check < current_time_minus_delta:
                connected_device.is_connected = False
                connected_device.save()
        serializer = DeviceSerializer(devices, many=True)
        return JsonResponse(serializer.data,  safe=False)
