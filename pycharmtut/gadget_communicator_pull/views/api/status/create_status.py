from django.http import JsonResponse
from rest_framework import generics, status, permissions
import json

from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.constants.water_constants import DEVISES, DEVICE_ID, STATUS_TIME
from gadget_communicator_pull.helpers import time_keeper
from gadget_communicator_pull.helpers.from_to_json_serializer import remove_device_field_from_json
from gadget_communicator_pull.models import Device, Status
from gadget_communicator_pull.water_serializers.status_serializer import StatusSerializer


class ApiCreateStatus(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        st = Status(execution_status=True, message='random status')
        serializer = StatusSerializer(instance=st)
        print(f'created status: {serializer.data}')

        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        print(body_data)
        body_data_copy = body_data.copy()
        json_without_device_field = remove_device_field_from_json(body_data_copy)
        serializer = StatusSerializer(data=json_without_device_field)
        if serializer.is_valid():
            status_el = serializer.save()
        else:
            print(serializer.errors)
            return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                data={'status': 'false',
                                      'unsupported_format': 'Form is not valid'})

        devices_len = len(body_data[DEVISES])

        if devices_len > 1:
            return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                data={'status': 'false',
                                      'unsupported_format': 'You must provide only one obj in devices '
                                                            'as  execute_only_once field included'})

        print(f'devices_len {devices_len}')

        for id in range(devices_len):
            device_obj = get_object_or_404(Device, device_id=body_data[DEVISES][id][DEVICE_ID])
            if device_obj.owner != request.user:
                return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                    data={'status': 'false', 'message': "No such device for user"})
            status_el.statuses.add(device_obj)
        date_k = time_keeper.TimeKeeper(time_keeper.TimeKeeper.get_current_date())
        status_el.status_time = date_k.get_current_time()
        status_el.save(update_fields=[STATUS_TIME])
        status_el.save()

        print(type(status_el))
        return JsonResponse(body_data)
