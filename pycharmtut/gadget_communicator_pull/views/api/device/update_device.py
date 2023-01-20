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
                value_ = body_data[key]
                device.water_level = value_
                if 100 < value_ or value_ < 1:
                    return self.return_bad_response(
                        f'water_level outside accepted boundaries {value_} ')
                device.save(update_fields=['water_level'])
            elif key == 'water_container_capacity':
                value_ = body_data[key]
                device.water_container_capacity = value_
                if 100000 < value_ or value_ < 100:
                    return self.return_bad_response(
                        f'water_container_capacity outside accepted boundaries {value_} ')
                device.save(update_fields=['water_container_capacity'])
            elif key == 'water_reset':
                device.water_reset = body_data[key]
                device.save(update_fields=['water_reset'])
            elif key == 'send_email':
                if body_data[key] == 'true':
                    device.send_email = True
                elif body_data[key] == 'false':
                    device.send_email = False
                if body_data[key]:
                    device.send_email = True
                elif not body_data[key]:
                    device.send_email = False
                device.save(update_fields=['send_email'])
            elif key == 'device_id':
                continue
            else:
                print("in")
                return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'false', 'unsupported_field': key})
        return JsonResponse(body_data)

    def return_bad_response(self, message):
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                            data={'status': 'false',
                                  'unsupported_format': message})
