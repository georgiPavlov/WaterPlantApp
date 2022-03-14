from django.http import JsonResponse
from rest_framework import generics, status

import requests
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.constants.photo_constants import PHOTO_CREATED
from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule


class ApiTakePhotoAsync(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        id_d = self.kwargs.get("id_d")
        device = get_object_or_404(Device, device_id=id_d)
        photo = PhotoModule.objects.create(photo_status=PHOTO_CREATED)
        photo.photos.add(device)
        photo.save()


        url = f"http://127.0.0.1:8080/gadget_communicator_pull/api/test_image/{photo.photo_id}"

        payload = "-----011000010111000001101001\r\nContent-Disposition: form-data; " \
                  "name=\"image_file\"; " \
                  "filename=\"Screenshot 2022-02-25 at 17.20.36.png\"\r\n" \
                  "Content-Type: " "image/png\r\n\r\n\r\n-----011000010111000001101001--\r\n "
        headers = {"Content-Type": "multipart/form-data; boundary=---011000010111000001101001"}

        response = requests.request("POST", url, data=payload, headers=headers)

        print(response.text)

        return JsonResponse(status=status.HTTP_201_CREATED,
                            data={'status': 'success', 'id': photo.photo_id})
