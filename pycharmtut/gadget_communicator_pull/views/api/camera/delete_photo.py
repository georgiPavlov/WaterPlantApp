from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule


class ApiDeletePhoto(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        print(id_)
        devices = Device.objects.filter(owner=request.user)
        pictures_for_user = PhotoModule.objects.filter(photos__in=devices)
        if not pictures_for_user:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                            'message': "No such status for user"})
        img = pictures_for_user.filter(photo_id=id_).first()
        if img is None:
            if not pictures_for_user:
                return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                            'message': "photo not found"})
        img.delete()
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
