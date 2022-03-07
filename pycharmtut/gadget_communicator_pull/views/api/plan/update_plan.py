import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status

from gadget_communicator_pull.constants.water_constants import WATER_PLAN_BASIC, WATER_PLAN_MOISTURE, WATER_PLAN_TIME, \
    DELETE_RUNNING_PLAN
from gadget_communicator_pull.models import Device, BasicPlan, TimePlan, MoisturePlan, WaterTime


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
        if 'name' not in body_unicode:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'key_not_found': 'name'})
        body_data = json.loads(body_unicode)
        print(body_data)
        name = body_data['name']
        plan = get_plan_for_name(name)

        if plan.plan_type is DELETE_RUNNING_PLAN:
            plan.water_volume = False
            plan.save(update_fields=['has_been_executed'])

        if plan is None:
            print(f'plan {plan}')
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'unsupported_field1': name})

        for key in body_data:
            print(type(key))
            if key == 'water_volume':
                plan.water_volume = body_data[key]
                plan.save(update_fields=['water_volume'])
            elif key == 'moisture_threshold' and plan.plan_type is WATER_PLAN_MOISTURE:
                plan.water_level = body_data[key]
                plan.save(update_fields=['moisture_threshold'])
            elif key == 'water_times' and plan.plan_type is WATER_PLAN_TIME:
                print("water_times")
                water_times_len = len(body_data['water_times'])
                water_times_list = []
                for id in range(water_times_len):
                    water_time_obj = get_object_or_404(WaterTime, device_id=body_data['water_times'][id])
                    water_times_list.append(water_time_obj)
                plan.water_times.all().delete()
                for el in water_times_list:
                    plan.water_times.add(el)
                    plan.save()
            elif key == 'has_been_executed':
                plan.water_volume = body_data[key]
                plan.save(update_fields=['has_been_executed'])
            elif key == 'execute_only_once' and plan.plan_type is WATER_PLAN_TIME:
                plan.water_volume = body_data[key]
                plan.save(update_fields=['execute_only_once'])
            elif key == 'name':
                continue
            elif key == 'plan_type':
                continue
            else:
                print("in")
                return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                    data={'status': 'false', 'unsupported_field': key})
        return JsonResponse(body_data)
