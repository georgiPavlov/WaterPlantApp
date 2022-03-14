import os
import mimetypes
from fileinput import filename
from wsgiref.util import FileWrapper

from django.http import HttpResponse, Http404
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models.photo_module import PhotoModule

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ApiDownloadPhoto(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        print(id_)
        photo = get_object_or_404(PhotoModule, photo_id=id_)
        print(f'base {BASE_DIR}')
        img = photo

        # wrapper = FileWrapper(open(f'/Users/i336317/PycharmProjects/pythonProject10/pycharmtut{img.image.url}'))
        # content_type = mimetypes.guess_type(f'/Users/i336317/PycharmProjects/pythonProject10/pycharmtut{img.image.url}')[0]
        # response = HttpResponse(wrapper, content_type=content_type)
        # response['Content-Length'] = os.path.getsize(f'/Users/i336317/PycharmProjects/pythonProject10/pycharmtut{img.image.url}')
        # response['Content-Disposition'] = "attachment; filename=%s" % f'/Users/i336317/PycharmProjects/pythonProject10/pycharmtut{img.image.url}'
        # return response
        imagePath = f'/Users/i336317/PycharmProjects/pythonProject10/pycharmtut{img.image.url}'
        file_path = os.path.join(imagePath)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                content_type = \
                    mimetypes.guess_type(f'/Users/i336317/PycharmProjects/pythonProject10/pycharmtut{img.image.url}')[0]
                response = HttpResponse(fh.read(), content_type=content_type)
                response['Content-Disposition'] = 'inline; filename=' + file_path
                return response
        raise Http404
