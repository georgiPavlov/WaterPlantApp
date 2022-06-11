import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework import status

from gadget_communicator_pull.models import Device


class ApiUpdateDevice(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        print(body_data)
        device = get_object_or_404(Device, device_id=body_data['device_id'])
        owner = request.user
        if device.owner != owner:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "No such device for user"})
        for key in body_data:
            print(type(key))
            if key == 'label':
                device.label = body_data[key]
                device.save(update_fields=['label'])
            elif key == 'water_level':
                device.water_level = body_data[key]
                device.save(update_fields=['water_level'])
            elif key == 'water_container_capacity':
                device.water_level = body_data[key]
                device.save(update_fields=['water_container_capacity'])
            elif key == 'water_reset':
                device.water_reset = body_data[key]
                device.save(update_fields=['water_reset'])
            elif key == 'device_id':
                continue
            else:
                print("in")
                return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false', 'unsupported_field': key})
        return JsonResponse(body_data)
