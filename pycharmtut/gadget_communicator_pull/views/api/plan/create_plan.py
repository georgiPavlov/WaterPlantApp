from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
import json

from gadget_communicator_pull.constants.water_constants import PLAN_TYPE, WATER_PLAN_TIME, WATER_PLAN_BASIC, \
    WATER_PLAN_MOISTURE, DEVICE_ID, DEVISES, PLAN_NAME
from gadget_communicator_pull.helpers.from_to_json_serializer import remove_device_field_from_json
from gadget_communicator_pull.models import Device, BasicPlan, TimePlan, MoisturePlan

from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer
from gadget_communicator_pull.water_serializers.time_plan_serializer import TimePlanSerializer
from gadget_communicator_pull.water_serializers.moisture_plan_serializer import MoisturePlanSerializer


def validate_for_duplicate(name):
    basic_plans = BasicPlan.objects.filter(name=name).first()
    time_plans = TimePlan.objects.filter(name=name).first()
    moisture_plans = MoisturePlan.objects.filter(name=name).first()

    if basic_plans is None and time_plans is None and moisture_plans is None:
        return True
    return False


class ApiCreatePlan(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        name = body_data.get(PLAN_NAME)

        if validate_for_duplicate(name=body_data):
            return JsonResponse(status=status.HTTP_403_FORBIDDEN, data={'status': 'false', 'duplicate_plan': name})

        if PLAN_TYPE not in body_data:
            print("key not in found in json")
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'plan_key_not_found': PLAN_TYPE})

        if any(DEVICE_ID not in s for s in body_data[DEVISES]):
            print(type(body_data[DEVISES]))
            print(body_data[DEVISES])
            print("key not in found in json")
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'plan_key_not_found': DEVICE_ID})

        plan_type = body_data[PLAN_TYPE]
        if WATER_PLAN_BASIC == plan_type:
            print(f'water type: {WATER_PLAN_BASIC}')
            body_data_copy = body_data.copy()
            json_without_device_field = remove_device_field_from_json(body_data_copy)
            serializer = BasePlanSerializer(data=json_without_device_field)
            serializer.is_valid()
            status_el = serializer.save()

            devices_len = len(body_data[DEVISES])
            for id in range(devices_len):
                device_obj = get_object_or_404(Device, device_id=body_data[DEVISES][id][DEVICE_ID])
                status_el.devices_b.add(device_obj)
            status_el.save()

        elif WATER_PLAN_MOISTURE == plan_type:
            print(f'water type: {WATER_PLAN_MOISTURE}')
            body_data_copy = body_data.copy()
            json_without_device_field = remove_device_field_from_json(body_data_copy)
            serializer = MoisturePlanSerializer(data=json_without_device_field)
            serializer.is_valid()
            status_el = serializer.save()

            devices_len = len(body_data[DEVISES])
            for id in range(devices_len):
                device_obj = get_object_or_404(Device, device_id=body_data[DEVISES][id][DEVICE_ID])
                status_el.devices_m.add(device_obj)
            status_el.save()

        elif WATER_PLAN_TIME == plan_type:
            print(f'water type: {WATER_PLAN_TIME}')
            body_data_copy = body_data.copy()
            json_without_device_field = remove_device_field_from_json(body_data_copy)
            serializer = TimePlanSerializer(data=json_without_device_field)
            serializer.is_valid()
            status_el = serializer.save()

            devices_len = len(body_data[DEVISES])
            for id in range(devices_len):
                device_obj = get_object_or_404(Device, device_id=body_data[DEVISES][id][DEVICE_ID])
                status_el.devices_t.add(device_obj)
            status_el.save()

        elif WATER_PLAN_TIME is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'unsupported_plan': plan_type})
        else:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'unsupported_plan': plan_type})
        return JsonResponse(body_data)
