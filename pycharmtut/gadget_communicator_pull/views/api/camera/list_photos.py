from django.http import JsonResponse
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule
from gadget_communicator_pull.water_serializers.photo_serializer import PhotoSerializer


class ApiListPhotos(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_d = self.kwargs.get("id_d")
        devices = Device.objects.filter(owner=request.user)
        device = devices.filter(device_id=id_d).first()
        if device is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "photo not found for user"})
        photos = PhotoModule.objects.filter(photos=device)
        serializer = PhotoSerializer(photos, many=True)

        return JsonResponse(serializer.data, safe=False)
