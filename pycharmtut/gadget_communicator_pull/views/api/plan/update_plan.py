import json

from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework import status

from gadget_communicator_pull.constants.water_constants import WATER_PLAN_MOISTURE, WATER_PLAN_TIME, \
    DELETE_RUNNING_PLAN, EXECUTION_PROPERTY, PLAN_HAS_BEEN_EXECUTED, PLAN_WATER_VOLUME, PLAN_MOISTURE_THRESHOLD, \
    PLAN_NAME, PLAN_TYPE, PLAN_MOISTURE_CHECK_INTERVAL, PLAN_MOISTURE_WEEKDAY_TIMES, \
    TIME_PLAN_TIMES, TIME_WEEKDAY, TIME_WATER, IS_RUNNING, PLAN_TO_STOP
from gadget_communicator_pull.helpers.helper import WEEKDAYS_NUMERIC
from gadget_communicator_pull.models import WaterTime, Device


def get_plan_for_name(name, devices):
    for device in devices:
        plans_b = device.device_relation_b.all()
        plans_t = device.device_relation_t.all()
        plans_m = device.device_relation_m.all()
        basic_plan = plans_b.filter(name=name).first()
        time_plan = plans_t.filter(name=name).first()
        moisture_plan = plans_m.filter(name=name).first()

        if basic_plan is not None:
            return basic_plan
        elif time_plan is not None:
            return time_plan
        elif moisture_plan is not None:
            return moisture_plan
    return None


def get_device_for_name(name, devices):
    for device in devices:
        plans_b = device.device_relation_b.all()
        plans_t = device.device_relation_t.all()
        plans_m = device.device_relation_m.all()
        basic_plan = plans_b.filter(name=name).first()
        time_plan = plans_t.filter(name=name).first()
        moisture_plan = plans_m.filter(name=name).first()

        if basic_plan is not None:
            return device
        elif time_plan is not None:
            return device
        elif moisture_plan is not None:
            return device
    return None


def return_bad_response(message):
    return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                        data={'status': 'false',
                              'unsupported_format': message})


class ApiUpdatePlan(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        if PLAN_NAME not in body_unicode:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'key_not_found': PLAN_NAME})
        body_data = json.loads(body_unicode)
        print(body_data)
        name = body_data[PLAN_NAME]
        devices = Device.objects.filter(owner=request.user)
        plan = get_plan_for_name(name, devices=devices)

        if name == 'default_stop' and body_data[PLAN_TYPE] == DELETE_RUNNING_PLAN and plan is None:
            plan_to_stop = body_data[PLAN_TO_STOP]
            plan = get_plan_for_name(plan_to_stop, devices=devices)
        if plan is None:
            print(f'plan {plan}')
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'unsupported_field1': name})
        if body_data[PLAN_TYPE] == DELETE_RUNNING_PLAN:
            if plan.plan_type == WATER_PLAN_MOISTURE or plan.plan_type == WATER_PLAN_TIME \
                    or plan.plan_type == DELETE_RUNNING_PLAN:
                print(f"is running {plan.is_running}")
                if plan.is_running:
                    print("plan is currently running")
                    plan.is_running = False
                    plan.save(update_fields=[IS_RUNNING])
                    plan.has_been_executed = False
                    plan.save(update_fields=[PLAN_HAS_BEEN_EXECUTED])
                    plan.plan_type = DELETE_RUNNING_PLAN
                    plan.save(update_fields=[PLAN_TYPE])
                else:
                    print("plan is not currently running")
                    return JsonResponse(status=status.HTTP_403_FORBIDDEN,
                                        data={'status': 'false', 'message': 'plan is not currently running'})
            else:
                print("basic plan does not have such field")
                return JsonResponse(status=status.HTTP_403_FORBIDDEN,
                                    data={'status': 'true', 'message': 'basic plan does not have such field'})
        plan_to_stop = body_data[PLAN_TO_STOP]
        device_obj = get_device_for_name(plan_to_stop, devices=devices)
        for key in body_data:
            if key == PLAN_TO_STOP:
                print("true..")
            elif key == PLAN_WATER_VOLUME:
                key_ = PLAN_WATER_VOLUME
                value_ = body_data[key_]
                if device_obj.water_container_capacity < value_ < 10:
                    return return_bad_response(
                        f'{key_} outside accepted boundaries: '
                        f'{device_obj.water_container_capacity} < {value_} < 10')
                plan.water_volume = body_data[key]
                plan.save(update_fields=[PLAN_WATER_VOLUME])
            elif key == PLAN_MOISTURE_THRESHOLD and plan.plan_type == WATER_PLAN_MOISTURE:
                print('moist plan')
                key_ = 'moisture_threshold'
                value_ = body_data[key_]
                if 100 < value_ < 1:
                    return return_bad_response(
                        f'{key_} outside accepted boundaries: '
                        f'100 < {value_} < 10')
                plan.moisture_threshold = body_data[key]
                plan.save(update_fields=[PLAN_MOISTURE_THRESHOLD])
            elif key == PLAN_MOISTURE_CHECK_INTERVAL and plan.plan_type == WATER_PLAN_MOISTURE:
                key_ = 'check_interval'
                value_ = body_data[key_]
                one_day_in_minutes = 1440
                if one_day_in_minutes < value_ < 1:
                    return return_bad_response(
                        f'{key_} outside accepted boundaries: '
                        f'{one_day_in_minutes} < {value_} < 1')
                plan.check_interval = body_data[key]
                plan.save(update_fields=[PLAN_MOISTURE_CHECK_INTERVAL])
            elif key == PLAN_MOISTURE_WEEKDAY_TIMES and plan.plan_type == WATER_PLAN_TIME:
                print(PLAN_MOISTURE_WEEKDAY_TIMES)
                water_times_len = len(body_data[PLAN_MOISTURE_WEEKDAY_TIMES])
                water_times_list = []
                for id in range(water_times_len):
                    weekday = body_data[TIME_PLAN_TIMES][id][TIME_WEEKDAY]
                    time_water = body_data[TIME_PLAN_TIMES][id][TIME_WATER]
                    if weekday in WEEKDAYS_NUMERIC.keys():
                        print(f"Key exists {weekday}")
                        weekday_num = WEEKDAYS_NUMERIC[weekday]
                    else:
                        print(f"Key does not exist {weekday}")
                        return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                            data={'status': 'false', 'unsupported_weekday_field': weekday})
                    water_time_obj = WaterTime(weekday=weekday_num, time_water=time_water, is_in_use=True)
                    water_times_list.append(water_time_obj)
                plan.water_times.all().delete()
                for el in water_times_list:
                    el.save()
                    plan.water_times.add(el)
                    plan.save()
            elif key == PLAN_HAS_BEEN_EXECUTED:
                plan.has_been_executed = body_data[key]
                plan.save(update_fields=[PLAN_HAS_BEEN_EXECUTED])
            elif key == EXECUTION_PROPERTY and plan.plan_type == WATER_PLAN_TIME:
                weekday_times_len = len(body_data['weekday_times'])
                if key == EXECUTION_PROPERTY and weekday_times_len > 1:
                    return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                        data={'status': 'false',
                                              'unsupported_format': 'You must provide only one obj in weekday_times '
                                                                    'as  execute_only_once field included'})
                plan.execute_only_once = body_data[key]
                plan.save(update_fields=[EXECUTION_PROPERTY])
            elif key == PLAN_NAME:
                continue
            elif key == PLAN_TYPE:
                continue
            else:
                print(f'unsupported_field: {key}')
                return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                    data={'status': 'false', 'unsupported_field': key})
        return JsonResponse(body_data)
