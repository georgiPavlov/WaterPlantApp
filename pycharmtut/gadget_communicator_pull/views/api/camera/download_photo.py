import os
import mimetypes
from fileinput import filename
from wsgiref.util import FileWrapper

from django.http import HttpResponse, Http404
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models.photo_module import PhotoModule
from pycharmtut.settings import MEDIA_ROOT_BASE


class ApiDownloadPhoto(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        img = get_object_or_404(PhotoModule, photo_id=id_)
        image_path = f'{MEDIA_ROOT_BASE}{img.image.url}'
        print(f'image path: {image_path}')
        file_path = os.path.join(image_path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                print('opening photo')
                content_type = mimetypes.guess_type(image_path)[0]
                print(f'content_type {content_type}')
                response = HttpResponse(fh.read(), content_type=content_type)
                response['Content-Disposition'] = "attachment; filename=%s" % file_path
                return response
        raise Http404
