import os
import mimetypes
from fileinput import filename
from wsgiref.util import FileWrapper

from django.http import HttpResponse, Http404, JsonResponse
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule
from pycharmtut.settings import MEDIA_ROOT_BASE


class ApiDownloadPhoto(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        devices = Device.objects.filter(owner=request.user)
        pictures_for_user = PhotoModule.objects.filter(photos__in=devices)
        if not pictures_for_user:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "No photos for user"})
        img = pictures_for_user.filter(photo_id=id_)[:1].get()
        if img is None:
            if not pictures_for_user:
                return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                            'message': "photo not found"})
        if img.photo_status != 'Ready':
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "Photo is not ready for download"})
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
                response['Access-Control-Allow-Origin'] = "*"

                response["Access-Control-Allow-Credentials"] = "true"
                response["Access-Control-Allow-Methods"] = "GET,HEAD,OPTIONS,POST,PUT"
                response["Access-Control-Allow-Headers"] = "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"
                return response
        raise Http404
