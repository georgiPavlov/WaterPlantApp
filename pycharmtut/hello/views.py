from django.shortcuts import render
from django.http import HttpResponse, request
from django.http import JsonResponse
from rest_framework.views import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
import sys
import json


# Create your views here.


class GetPlan(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        plan = {"name": "plant1","type": "basic","water_volum": "200ml"}

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


def hello_view(*args, **kwargs):
    return JsonResponse({'foo': 'bar'})
