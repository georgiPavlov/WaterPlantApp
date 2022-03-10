from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from gadget_communicator_pull.models import Device, Status
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer
from gadget_communicator_pull.water_serializers.status_serializer import StatusSerializer


class ApiGetStatus(DetailView):
    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        status = get_object_or_404(Status, status_id=id_)
        serializer = StatusSerializer(status)
        return JsonResponse(serializer.data)
