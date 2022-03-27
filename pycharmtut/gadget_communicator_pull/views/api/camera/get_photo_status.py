from django.http import JsonResponse
from rest_framework import generics, permissions, status

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule
from gadget_communicator_pull.water_serializers.photo_serializer import PhotoSerializer


class ApiGetPhoto(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        devices = Device.objects.filter(owner=request.user)
        pictures_for_user = PhotoModule.objects.filter(photos__in=devices)
        if not pictures_for_user:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "No photos for user"})
        img = pictures_for_user.filter(photo_id=id_).first()
        if img is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                            'message': "photo not found"})
        serializer = PhotoSerializer(img)
        return JsonResponse(serializer.data)
