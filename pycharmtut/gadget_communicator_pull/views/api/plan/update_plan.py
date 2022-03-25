import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status

from gadget_communicator_pull.constants.water_constants import WATER_PLAN_MOISTURE, WATER_PLAN_TIME, \
    DELETE_RUNNING_PLAN, EXECUTION_PROPERTY, PLAN_HAS_BEEN_EXECUTED, PLAN_WATER_VOLUME, PLAN_MOISTURE_THRESHOLD, \
    PLAN_MOISTURE_WATER_TIMES, PLAN_NAME, PLAN_TYPE, PLAN_MOISTURE_CHECK_INTERVAL, PLAN_MOISTURE_WEEKDAY_TIMES, \
    TIME_PLAN_TIMES, TIME_WEEKDAY, TIME_WATER, IS_RUNNING
from gadget_communicator_pull.helpers.helper import WEEKDAYS_NUMERIC
from gadget_communicator_pull.models import BasicPlan, TimePlan, MoisturePlan, WaterTime
from gadget_communicator_pull.water_serializers.time_plan_serializer import WaterTimeSerializer


def get_plan_for_name(name):
    basic_plan = BasicPlan.objects.filter(name=name).first()
    time_plan = TimePlan.objects.filter(name=name).first()
    moisture_plan = MoisturePlan.objects.filter(name=name).first()

    if basic_plan is not None:
        return basic_plan
    elif time_plan is not None:
        return time_plan
    elif moisture_plan is not None:
        return moisture_plan
    return None


class ApiUpdatePlan(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        if PLAN_NAME not in body_unicode:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'key_not_found': PLAN_NAME})
        body_data = json.loads(body_unicode)
        print(body_data)
        name = body_data[PLAN_NAME]
        plan = get_plan_for_name(name)

        if plan is None:
            print(f'plan {plan}')
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'unsupported_field1': name})

        if body_data[PLAN_TYPE] == DELETE_RUNNING_PLAN:
            if plan.plan_type == WATER_PLAN_MOISTURE or plan.plan_type == WATER_PLAN_TIME:
                if plan.is_running:
                    print("plan is currently running")
                    plan.is_running = False
                    plan.save(update_fields=[IS_RUNNING])
                    plan.has_been_executed = True
                    plan.save(update_fields=[PLAN_HAS_BEEN_EXECUTED])

                else:
                    print("plan is not currently running")
                    return JsonResponse(status=status.HTTP_403_FORBIDDEN,
                                        data={'status': 'false', 'message': 'plan is not currently running'})
            else:
                print("basic plan does not have such field")
                return JsonResponse(status=status.HTTP_403_FORBIDDEN,
                                    data={'status': 'true', 'message': 'basic plan does not have such field'})

        for key in body_data:
            print(type(key))
            print(f'key: {key}')
            print(f'plan: {plan.plan_type}')
            if key == PLAN_MOISTURE_THRESHOLD:
                print("true..")
            if key == PLAN_WATER_VOLUME:
                plan.water_volume = body_data[key]
                plan.save(update_fields=[PLAN_WATER_VOLUME])
            elif key == PLAN_MOISTURE_THRESHOLD and plan.plan_type == WATER_PLAN_MOISTURE:
                plan.moisture_threshold = body_data[key]
                plan.save(update_fields=[PLAN_MOISTURE_THRESHOLD])
            elif key == PLAN_MOISTURE_CHECK_INTERVAL and plan.plan_type == WATER_PLAN_MOISTURE:
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
                plan.water_volume = body_data[key]
                plan.save(update_fields=[PLAN_HAS_BEEN_EXECUTED])
            elif key == EXECUTION_PROPERTY and plan.plan_type == WATER_PLAN_TIME:
                plan.water_volume = body_data[key]
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
