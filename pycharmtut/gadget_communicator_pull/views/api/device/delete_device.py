from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework import status

from gadget_communicator_pull.models import Device


class ApiDeleteDevice(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        device = get_object_or_404(Device, device_id=id_)
        owner = request.user
        if device.owner != owner:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "No such device for user"})
        Device.objects.get(device_id=id_).delete()
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
