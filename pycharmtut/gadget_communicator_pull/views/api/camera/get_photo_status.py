from django.http import JsonResponse
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models.photo_module import PhotoModule
from gadget_communicator_pull.water_serializers.photo_serializer import PhotoSerializer


class ApiGetPhoto(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        print(id_)
        device = get_object_or_404(PhotoModule, photo_id=id_)
        serializer = PhotoSerializer(device)
        return JsonResponse(serializer.data)
