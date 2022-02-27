from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework import generics
import sys
import json

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer
from gadget_communicator_pull.water_serializers.constants.water_constants import DEVICE, WATER_LEVEL, \
    MOISTURE_LEVEL, EXECUTION_STATUS, EXECUTION_MESSAGE

from gadget_communicator_pull.water_serializers.from_to_json_serializer import to_json_serializer, \
    remove_device_field_from_json
from gadget_communicator_pull.water_serializers.moisture_plan_serializer import MoisturePlanSerializer
from gadget_communicator_pull.water_serializers.status_serializer import StatusSerializer
from gadget_communicator_pull.water_serializers.time_plan_serializer import TimePlanSerializer


class DeviceObjectMixin(object):
    def get_device_guid(self, query_params):
        device_guid = None
        if DEVICE in query_params:
            print(f'{DEVICE} param specified')
            for param in query_params:
                print(f'param:  {param}')
            device_guid = query_params.get(DEVICE)
            print(f'device_guid:  {device_guid}')
        else:
            print(f'{DEVICE} param not specified')
            return None
        return device_guid

    def get_device(self, device_guid):
        return Device.objects.filter(device_id=device_guid).first()



class GetPlan(generics.GenericAPIView, DeviceObjectMixin):
    def get(self, request, *args, **kwargs):
        # plan = {"name": "plant1", "plan_type": "moisture", "water_volume": 200, "moisture_threshold": 0.8,
        #  "check_interval": 1}

        device_guid = self.get_device_guid(self.request.query_params)
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        device = self.get_device(device_guid)
        if device is None:
            print(f'no such device {device}')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        plan_json = None
        if device.device_relation_b is not None:
            print(f'Plan of type: {device.device_relation_b.plan_type}')
            plan = device.device_relation_b
            device.device_relation_b = None
            device.save()
            serializer = BasePlanSerializer(instance=plan)
            plan_json = to_json_serializer(serializer)
        elif device.device_relation_m is not None:
            print(f'Plan of type: {device.device_relationmb.plan_type}')
            plan = device.device_relation_m
            serializer = MoisturePlanSerializer(instance=plan)
            plan_json = to_json_serializer(serializer)
        elif device.device_relation_t is not None:
            plan = device.device_relation_t
            print(f'Plan of type: {device.device_relation_t.plan_type}')
            if plan.is_running is True:
                return HttpResponse(status=status.HTTP_204_NO_CONTENT)
                # delete plan
            device.device_relation_t = None
            device.save()
            serializer = TimePlanSerializer(instance=plan)
            plan_json = to_json_serializer(serializer)
        else:
            print('All plan relations are empty')

        if plan_json is None:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)

        print(type(plan_json))
        json_without_device_field = remove_device_field_from_json(plan_json)
        # plan1 = {"name": "plant1", "plan_type": "time_based", "water_volume": 200,
        #         "water_times": [{"weekday": "Friday", "time_water": "07:47 PM"}]}
        # plan1 = {"name": "plant1", "plan_type": "basic", "water_volume": 200}
        # plan = {"name": "plant1", "plan_type": "moisture", "water_volume": 200, "moisture_threshold": 0.8,
        #  "check_interval": 1}

        return JsonResponse(json_without_device_field, safe=False)


class PostWater(generics.CreateAPIView, DeviceObjectMixin):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        device_guid = body_data[DEVICE]
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        device = self.get_device(device_guid)
        if device is None:
            print(f'no such device {device}')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        print(body_data)

        device_guid = body_data[DEVICE]
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        water_level = body_data[WATER_LEVEL]
        if device_guid is None:
            print(f'water_level {water_level} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        device.water_level = water_level
        device.save()

        return JsonResponse(body_data)


class PostMoisture(generics.CreateAPIView, DeviceObjectMixin):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        device_guid = body_data[DEVICE]
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        device = self.get_device(device_guid)
        if device is None:
            print(f'no such device {device}')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        print(body_data)

        moisture_level = body_data[MOISTURE_LEVEL]
        if device_guid is None:
            print(f'moisture_level {moisture_level} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        device.moisture_level = moisture_level
        device.save()

        return JsonResponse(body_data)


class PostPlanExecution(generics.CreateAPIView, DeviceObjectMixin):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        device_guid = body_data[DEVICE]
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        device = self.get_device(device_guid)
        if device is None:
            print(f'no such device {device}')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        print(body_data)

        execution_status = body_data[EXECUTION_STATUS]
        if device_guid is None:
            print(f'execution_status {execution_status} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        execution_message = body_data[EXECUTION_MESSAGE]
        if device_guid is None:
            print(f'execution_message {execution_message} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        print(body_data)
        serializer = StatusSerializer(data=body_data)
        serializer.is_valid()
        status_el = serializer.save()
        print(type(status_el))


        device.status_relation = status_el
        device.save()
        return JsonResponse(body_data)

