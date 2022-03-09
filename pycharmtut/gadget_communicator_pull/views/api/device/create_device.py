from django.http import JsonResponse
from rest_framework import generics, status
import json

from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class ApiCreateDevice(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        print(body_data)
        serializer = DeviceSerializer(data=body_data)
        if serializer.is_valid():
            status_el = serializer.save()
        else:
            print(serializer.errors)
            return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                data={'status': 'false',
                                      'unsupported_format': 'Form is not valid'})
        print(type(status_el))
        return JsonResponse(body_data)
