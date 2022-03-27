from django.http import JsonResponse
from rest_framework import status, permissions, generics

from gadget_communicator_pull.models import BasicPlan, TimePlan, MoisturePlan, Device
from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer
from gadget_communicator_pull.water_serializers.moisture_plan_serializer import MoisturePlanSerializer
from gadget_communicator_pull.water_serializers.time_plan_serializer import TimePlanSerializer


def get_plan_for_name(name,devices):
    for device in devices:
        plans_b = device.device_relation_b.all()
        plans_t = device.device_relation_t.all()
        plans_m = device.device_relation_m.all()
        basic_plan = plans_b.filter(name=name).first()
        time_plan = plans_t.filter(name=name).first()
        moisture_plan = plans_m.filter(name=name).first()

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


class ApiGetPlansByDeviceId(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        devices_t = Device.objects.filter(owner=request.user)
        devices = devices_t.filter(device_id=id_)

        basic_plans = BasicPlan.objects.filter(devices_b__in=devices)
        time_plans = TimePlan.objects.filter(devices_t__in=devices)
        moisture_plans = MoisturePlan.objects.filter(devices_m__in=devices)

        basic_plans_json = BasePlanSerializer(basic_plans, many=True)
        time_plans_json = TimePlanSerializer(time_plans, many=True)
        moisture_plans_json = MoisturePlanSerializer(moisture_plans, many=True)

        plans_json = [basic_plans_json.data, time_plans_json.data, moisture_plans_json.data]

        return JsonResponse(plans_json,  safe=False)
