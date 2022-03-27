from django.http import JsonResponse
from rest_framework import generics, status, permissions

from gadget_communicator_pull.constants.photo_constants import PHOTO_CREATED
from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule


class ApiTakePhotoAsync(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_d = self.kwargs.get("id_d")
        devices = Device.objects.filter(owner=request.user)
        device = devices.filter(device_id=id_d).first()
        if device is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "photo not found for user"})
        photo = PhotoModule.objects.create(photo_status=PHOTO_CREATED)
        photo.photos.add(device)
        photo.save()
        return JsonResponse(status=status.HTTP_201_CREATED,
                            data={'status': 'success', 'id': photo.photo_id})
