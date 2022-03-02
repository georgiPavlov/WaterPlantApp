from django.http import JsonResponse
from rest_framework import generics
import json

from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class ApiCreateDevice(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        print(body_data)
        serializer = DeviceSerializer(data=body_data)
        serializer.is_valid()
        status_el = serializer.save()
        print(type(status_el))
        return JsonResponse(body_data)
