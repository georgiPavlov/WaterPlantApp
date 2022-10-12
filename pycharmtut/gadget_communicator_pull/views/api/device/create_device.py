from django.http import JsonResponse
from rest_framework import generics, status, permissions
import json

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class ApiCreateDevice(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        print(body_data)
        device_id = body_data['device_id']
        device = Device.objects.filter(device_id=device_id).first()
        if device is not None:
            return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                data={'status': 'false',
                                      'unsupported_format': f'Device with id {device_id} already exists'})

        serializer = DeviceSerializer(data=body_data)
        if serializer.is_valid():
            status_el = serializer.save()
            status_el.owner = request.user
            status_el.save()
        else:
            print(serializer.errors)
            return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                data={'status': 'false',
                                      'unsupported_format': 'Form is not valid'})
        print(type(status_el))
        return JsonResponse(body_data)
