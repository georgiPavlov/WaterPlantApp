from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status

from gadget_communicator_pull.constants.water_constants import WATER_PLAN_BASIC, WATER_PLAN_MOISTURE, WATER_PLAN_TIME
from gadget_communicator_pull.models import BasicPlan, TimePlan, MoisturePlan


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


def delete_plan_for_name(plan):
    plan_type = plan.plan_type
    name = plan.name

    if plan_type is WATER_PLAN_BASIC:
        BasicPlan.objects.get(name=name).delete()
    elif plan_type is WATER_PLAN_MOISTURE:
        TimePlan.objects.get(name=name).delete()
    elif plan_type is WATER_PLAN_TIME:
        MoisturePlan.objects.get(name=name).delete()


class ApiDeletePlan(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        name_ = self.kwargs.get("id")
        plan = get_plan_for_name(name=name_)

        if plan is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'plan not found'})

        delete_plan_for_name(plan)
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
