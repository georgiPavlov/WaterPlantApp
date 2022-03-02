from django.http import JsonResponse
from rest_framework import generics

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class ApiListDevices(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        devices = Device.objects.all()
        serializer = DeviceSerializer(devices, many=True)
        return JsonResponse(serializer.data,  safe=False)
