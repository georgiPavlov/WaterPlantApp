from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.constants.photo_constants import PHOTO_READY
from gadget_communicator_pull.models.photo_module import PhotoModule


class ApiCreatePhoto(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        print(id_)
        photo_el = get_object_or_404(PhotoModule, photo_id=id_)
        image_file = request.FILES.get('image_file')
        photo_el.image = image_file
       # photo_el.photo_status = PHOTO_READY
        photo_el.save()

        return JsonResponse(status=status.HTTP_200_OK,
                            data={'status': 'success'})
