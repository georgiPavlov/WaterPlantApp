import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status

from gadget_communicator_pull.constants.water_constants import WATER_PLAN_BASIC, WATER_PLAN_MOISTURE, WATER_PLAN_TIME
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
        body_data = json.loads(body_unicode)
        print(body_data)
        name = body_data['name']
        plan = get_plan_for_name(name)

        if plan is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                data={'status': 'false', 'unsupported_field': name})

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
                for id in range(water_times_len):
                    for water_time in plan.water_times:
                        plan.water_times.get(water_time).delete()


                    water_times_obj = get_object_or_404(WaterTime, device_id=body_data['water_times'][id][DEVICE_ID])
                    status_el.devices_m.add(device_obj)
            elif key == 'name':
                continue
            else:
                print("in")
                return JsonResponse(status=status.HTTP_404_NOT_FOUND,
                                    data={'status': 'false', 'unsupported_field': key})
        return JsonResponse(body_data)
