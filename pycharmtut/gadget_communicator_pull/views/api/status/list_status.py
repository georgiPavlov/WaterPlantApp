from django.http import JsonResponse
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models import Device, Status
from gadget_communicator_pull.water_serializers.status_serializer import StatusSerializer


class ApiListStatus(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        device = get_object_or_404(Device, device_id=id_)

        status = Status.objects.filter(statuses=device)
        serializer = StatusSerializer(status, many=True)
        return JsonResponse(serializer.data,  safe=False)
