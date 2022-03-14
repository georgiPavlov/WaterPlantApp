from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models.photo_module import PhotoModule


class ApiDeletePhoto(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        print(id_)
        get_object_or_404(PhotoModule, photo_id=id_)
        PhotoModule.objects.get(photo_id=id_).delete()
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
