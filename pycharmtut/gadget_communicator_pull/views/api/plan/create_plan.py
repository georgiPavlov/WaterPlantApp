from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework import status
import json

from gadget_communicator_pull.constants.water_constants import PLAN_TYPE, WATER_PLAN_TIME, WATER_PLAN_BASIC, \
    WATER_PLAN_MOISTURE, DEVICE_ID, DEVISES, PLAN_NAME, TIME_PLAN_TIMES, TIME_WEEKDAY, TIME_WATER, EXECUTION_PROPERTY
from gadget_communicator_pull.helpers.from_to_json_serializer import remove_device_field_from_json
from gadget_communicator_pull.helpers.helper import WEEKDAYS_NUMERIC
from gadget_communicator_pull.models import Device, BasicPlan, TimePlan, MoisturePlan, WaterTime

from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer
from gadget_communicator_pull.water_serializers.time_plan_serializer import TimePlanSerializer, WaterTimeSerializer
from gadget_communicator_pull.water_serializers.moisture_plan_serializer import MoisturePlanSerializer


def validate_for_duplicate(name, devices):
    for device in devices:
        plans_b = device.device_relation_b.all()
        plans_t = device.device_relation_t.all()
        plans_m = device.device_relation_m.all()
        basic_plan = plans_b.filter(name=name).first()
        time_plan = plans_t.filter(name=name).first()
        moisture_plan = plans_m.filter(name=name).first()
        if basic_plan is not None:
            return True
        if time_plan is not None:
            return True
        if moisture_plan is not None:
            return True
    return False


class ApiCreatePlan(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        name = body_data.get(PLAN_NAME)
        devices = Device.objects.filter(owner=request.user)
        print(body_data)
        if validate_for_duplicate(name=name, devices=devices):
            return JsonResponse(status=status.HTTP_403_FORBIDDEN, data={'status': 'false', 'duplicate_plan': name})

        if PLAN_TYPE not in body_data:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'plan_key_not_found': PLAN_TYPE})

        if any(DEVICE_ID not in s for s in body_data[DEVISES]):
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'plan_key_not_found': DEVICE_ID})

        plan_type = body_data[PLAN_TYPE]
        if WATER_PLAN_BASIC == plan_type:
            body_data_copy = body_data.copy()
            json_without_device_field = remove_device_field_from_json(body_data_copy)
            serializer = BasePlanSerializer(data=json_without_device_field)
            if serializer.is_valid():
                status_el = serializer.save()
            else:
                print(serializer.errors)
                return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                    data={'status': 'false',
                                          'unsupported_format': 'Form is not valid'})

            devices_len = len(body_data[DEVISES])
            for id in range(devices_len):
                device_obj = get_object_or_404(Device, device_id=body_data[DEVISES][id][DEVICE_ID])
                if device_obj.owner != request.user:
                    status_el.delete()
                    return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                        data={'status': 'false', 'message': "No such device for user"})

                value_ = body_data['water_volume']
                if device_obj.water_container_capacity >= value_ >= 10:
                    status_el.delete()
                    return self.return_bad_response(
                        f'water_volume outside accepted boundaries: '
                        f'{device_obj.water_container_capacity} <= {value_} >= 10')

                status_el.devices_b.add(device_obj)
            status_el.save()

        elif WATER_PLAN_MOISTURE == plan_type:
            body_data_copy = body_data.copy()
            json_without_device_field = remove_device_field_from_json(body_data_copy)
            serializer = MoisturePlanSerializer(data=json_without_device_field)
            if serializer.is_valid():
                status_el = serializer.save()
            else:
                print(serializer.errors)
                return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                    data={'status': 'false',
                                          'unsupported_format': 'Form is not valid'})

            devices_len = len(body_data[DEVISES])
            for id in range(devices_len):
                device_obj = get_object_or_404(Device, device_id=body_data[DEVISES][id][DEVICE_ID])
                if device_obj.owner != request.user:
                    status_el.delete()
                    return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                        data={'status': 'false', 'message': "No such device for user"})
                key_ = 'water_volume'
                value_ = body_data[key_]
                if device_obj.water_container_capacity >= value_ >= 10:
                    status_el.delete()
                    return self.return_bad_response(
                        f'{key_} outside accepted boundaries: '
                        f'{device_obj.water_container_capacity} <= {value_} >= 10')

                key_ = 'moisture_threshold'
                value_ = body_data[key_]
                if 100 >= value_ >= 1:
                    status_el.delete()
                    return self.return_bad_response(
                        f'{key_} outside accepted boundaries: '
                        f'100 <= {value_} >= 10')

                key_ = 'check_interval'
                value_ = body_data[key_]
                one_day_in_minutes = 1440
                if one_day_in_minutes >= value_ >= 1:
                    status_el.delete()
                    return self.return_bad_response(
                        f'{key_} outside accepted boundaries: '
                        f'{one_day_in_minutes} <= {value_} >= 1')

                status_el.devices_m.add(device_obj)
            status_el.save()

        elif WATER_PLAN_TIME == plan_type:
            if 'weekday_times' not in body_data:
                print("key not in found in json")
                return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                    data={'status': 'false', 'plan_key_not_found': 'weekday_times'})

            weekday_times_len = len(body_data['weekday_times'])
            if weekday_times_len == 0:
                return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                    data={'status': 'false',
                                          'unsupported_format': 'You must provide weekday_times obj'})

            for key in body_data:
                if key == EXECUTION_PROPERTY and weekday_times_len > 1:
                    return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                        data={'status': 'false',
                                              'unsupported_format': 'You must provide only one obj in weekday_times '
                                                                    'as  execute_only_once field included'})

            body_data_copy = body_data.copy()
            json_without_device_field = remove_device_field_from_json(body_data_copy)
            print(f'[time_plan] json for save: {json_without_device_field}')
            serializer = TimePlanSerializer(data=json_without_device_field)
            if serializer.is_valid():
                status_el = serializer.save()
            else:
                print(serializer.errors)
                return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                    data={'status': 'false',
                                          'unsupported_format': 'Form is not valid'})
            weekday_times_len = len(body_data[TIME_PLAN_TIMES])
            print(f'weekday_times {weekday_times_len}')
            for id in range(weekday_times_len):
                print(json_without_device_field[TIME_PLAN_TIMES][id])

                weekday = json_without_device_field[TIME_PLAN_TIMES][id][TIME_WEEKDAY]
                time_water = json_without_device_field[TIME_PLAN_TIMES][id][TIME_WATER]
                if weekday in WEEKDAYS_NUMERIC.keys():
                    print(f"Key exists {weekday}")
                    weekday_num = WEEKDAYS_NUMERIC[weekday]
                else:
                    print(f"Key does not exist {weekday}")
                    return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                        data={'status': 'false', 'unsupported_weekday_field': weekday})
                water_time_obj = WaterTime(weekday=weekday_num, time_water=time_water)
                water_time_obj.save()
                status_el.water_times.add(water_time_obj)
            status_el.save()

            devices_len = len(body_data[DEVISES])
            print(f'devices_len {devices_len}')
            for id in range(devices_len):
                device_obj = get_object_or_404(Device, device_id=body_data[DEVISES][id][DEVICE_ID])
                if device_obj.owner != request.user:
                    status_el.delete()
                    return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                        data={'status': 'false', 'message': "No such device for user"})
                value_ = body_data['water_volume']
                if device_obj.water_container_capacity >= value_ >= 10:
                    status_el.delete()
                    return self.return_bad_response(
                        f'water_volume outside accepted boundaries: '
                        f'{device_obj.water_container_capacity} <= {value_} >= 10')
                status_el.devices_t.add(device_obj)
            status_el.save()

        elif WATER_PLAN_TIME is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'unsupported_plan': plan_type})
        else:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'unsupported_plan': plan_type})
        return JsonResponse(body_data)


    def return_bad_response(self, message):
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                            data={'status': 'false',
                                  'unsupported_format': message})
