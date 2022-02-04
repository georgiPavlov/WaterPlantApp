from django.shortcuts import render
from django.http import HttpResponse, request
from django.http import JsonResponse
from rest_framework.views import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
import sys
import json


class GetPlan(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        # plan = {"name": "plant1", "plan_type": "basic", "water_volume": 200}
        #plan = {"name": "plant1", "plan_type": "moisture", "water_volume": 200, "moisture_threshold": 0.8,
              #  "check_interval": 1}
        plan = {"name": "plant1", "plan_type": "time_based", "water_volume": 200,
                "water_times":[{"weekday": "Friday", "time_water": "10:30 PM"}]}
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


def hello_view(*args, **kwargs):
    return JsonResponse({'foo': 'bar'})
