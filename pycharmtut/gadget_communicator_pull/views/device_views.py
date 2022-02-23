from django.http import JsonResponse
from rest_framework import generics
import sys
import json
import gadget_communicator_pull.water_serializers.base_plan_serializer
import gadget_communicator_pull.water_serializers.time_plan_serializer
import gadget_communicator_pull.water_serializers.moisture_plan_serializer
import gadget_communicator_pull.water_serializers.device_serializer



class GetPlan(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        # plan = {"name": "plant1", "plan_type": "basic", "water_volume": 200}
        # plan = {"name": "plant1", "plan_type": "moisture", "water_volume": 200, "moisture_threshold": 0.8,
        #  "check_interval": 1}
        plan = {"name": "plant1", "plan_type": "time_based", "water_volume": 200,
                "water_times": [{"weekday": "Friday", "time_water": "07:47 PM"}]}

        return JsonResponse(plan, safe=False)


class PostWater(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        var = '"%s"' % request.body
        original_stdout = sys.stdout
        with open('/tmp/filenameWater.txt', 'a') as f:
            sys.stdout = f
            print(var)
            sys.stdout = original_stdout
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        return JsonResponse(body_data)


class PostMoisture(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        var = 'Raw Data: "%s"' % request.body
        original_stdout = sys.stdout
        with open('/tmp/filenameMoisture.txt', 'w') as f:
            sys.stdout = f
            print(var)
            sys.stdout = original_stdout
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        return JsonResponse(body_data)


class PostPlanExecution(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        var = 'Raw Data: "%s"' % request.body
        original_stdout = sys.stdout
        with open('/tmp/filenameStatus.txt', 'w') as f:
            sys.stdout = f
            print(var)
            sys.stdout = original_stdout
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        return JsonResponse(body_data)


class PostStatus(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        var = 'Raw Data: "%s"' % request.body
        original_stdout = sys.stdout
        with open('/tmp/filenameStatus.txt', 'w') as f:
            sys.stdout = f
            print(var)
            sys.stdout = original_stdout
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        return JsonResponse(body_data)