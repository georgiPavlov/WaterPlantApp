from django.http import JsonResponse
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule
from gadget_communicator_pull.water_serializers.photo_serializer import PhotoSerializer


class ApiListPhotos(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        id_d = self.kwargs.get("id_d")
        device = get_object_or_404(Device, device_id=id_d)
        photos = PhotoModule.objects.filter(photos=device)
        serializer = PhotoSerializer(photos, many=True)

        return JsonResponse(serializer.data, safe=False)
