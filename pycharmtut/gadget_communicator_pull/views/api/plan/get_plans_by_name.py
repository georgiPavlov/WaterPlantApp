from django.http import JsonResponse
from django.views.generic import DetailView
from rest_framework import status

from gadget_communicator_pull.models import BasicPlan, TimePlan, MoisturePlan
from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer
from gadget_communicator_pull.water_serializers.moisture_plan_serializer import MoisturePlanSerializer
from gadget_communicator_pull.water_serializers.time_plan_serializer import TimePlanSerializer


def get_plan_for_name(name):
    basic_plan = BasicPlan.objects.filter(name=name).first()
    time_plan = TimePlan.objects.filter(name=name).first()
    moisture_plan = MoisturePlan.objects.filter(name=name).first()

    if basic_plan is not None:
        serializer = BasePlanSerializer(basic_plan)
        return serializer.data
    elif time_plan is not None:
        serializer = MoisturePlanSerializer(basic_plan)
        return serializer.data
    elif moisture_plan is not None:
        serializer = TimePlanSerializer(basic_plan)
        return serializer.data
    return None


class ApiGetPlansByName(DetailView):
    def get(self, request, *args, **kwargs):
        name_ = self.kwargs.get("id")
        plan = get_plan_for_name(name=name_)

        if plan is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'plan not found'})

        return JsonResponse(plan)
