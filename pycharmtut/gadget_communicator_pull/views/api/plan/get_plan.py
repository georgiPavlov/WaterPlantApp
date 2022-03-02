from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class ApiGetDevice(DetailView):
    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        device = get_object_or_404(Device, device_id=id_)
        serializer = DeviceSerializer(device)
        return JsonResponse(serializer.data)
