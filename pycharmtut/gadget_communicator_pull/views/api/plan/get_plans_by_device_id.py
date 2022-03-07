from django.http import JsonResponse
from django.views.generic import DetailView
from rest_framework import status

from gadget_communicator_pull.models import BasicPlan, TimePlan, MoisturePlan
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


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


class ApiGetPlansByDeviceId(DetailView):
    def get(self, request, *args, **kwargs):
        name_ = self.kwargs.get("id")
        plan = get_plan_for_name(name=name_)

        if plan is None:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND, data={'status': 'plan not found'})

        serializer = DeviceSerializer(plan)
        return JsonResponse(serializer.data)
