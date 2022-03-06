from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status

from gadget_communicator_pull.models import Device


class ApiDeleteDevice(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        get_object_or_404(Device, device_id=id_)
        Device.objects.get(device_id=id_).delete()
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
