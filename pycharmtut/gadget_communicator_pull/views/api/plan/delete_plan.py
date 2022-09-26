import logging

from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework import status

from gadget_communicator_pull.constants.water_constants import WATER_PLAN_BASIC, WATER_PLAN_MOISTURE, WATER_PLAN_TIME
from gadget_communicator_pull.models import BasicPlan, TimePlan, MoisturePlan, Device


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


def delete_plan_for_name(plan):
    plan_type = plan.plan_type
    name = plan.name
    print('test ' + name)
    print('plan type ' + plan_type)
    if plan_type == WATER_PLAN_BASIC:
        print('test2 ' + WATER_PLAN_TIME + '   ' + name)
        BasicPlan.objects.get(name=name).delete()
    elif plan_type == WATER_PLAN_TIME:
        print('test2 ' + WATER_PLAN_TIME + '   ' + name)
        TimePlan.objects.get(name=name).delete()
    elif plan_type == WATER_PLAN_MOISTURE:
        print('test2 ' + WATER_PLAN_TIME + '   ' + name)
        MoisturePlan.objects.get(name=name).delete()


class ApiDeletePlan(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        devices = Device.objects.filter(owner=request.user)

        name_ = self.kwargs.get("id")
        plan = get_plan_for_name(name=name_, devices=devices)

        if plan is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'plan not found'})
        delete_plan_for_name(plan)
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
