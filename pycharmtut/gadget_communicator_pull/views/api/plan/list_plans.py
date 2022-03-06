from django.http import JsonResponse
from rest_framework import generics
import json as simplejson

from gadget_communicator_pull.models import Device, BasicPlan, TimePlan, MoisturePlan
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer
from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer
from gadget_communicator_pull.water_serializers.moisture_plan_serializer import MoisturePlanSerializer
from gadget_communicator_pull.water_serializers.time_plan_serializer import TimePlanSerializer


class ApiListPlans(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        devices = Device.objects.all()
        basic_plans = BasicPlan.objects.filter(devices_b__in=devices)
        time_plans = TimePlan.objects.filter(devices_t__in=devices)
        moisture_plans = MoisturePlan.objects.filter(devices_m__in=devices)

        basic_plans_json = BasePlanSerializer(basic_plans, many=True)
        time_plans_json = TimePlanSerializer(time_plans, many=True)
        moisture_plans_json = MoisturePlanSerializer(moisture_plans, many=True)

        plans_json = [basic_plans_json.data, time_plans_json.data, moisture_plans_json.data]

        return JsonResponse(plans_json,  safe=False)
