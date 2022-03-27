from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, generics

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class ApiGetDevice(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        device = get_object_or_404(Device, device_id=id_)
        print(f'owner {request.user}')
        print(f'owner1 {device.owner}')
        if device.owner != request.user:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false', 'message': "No such device for user"})
        serializer = DeviceSerializer(device)
        return JsonResponse(serializer.data)
