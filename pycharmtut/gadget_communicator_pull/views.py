from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, request
from django.http import JsonResponse
from django.views import View
from rest_framework.views import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
import sys
import json
from .forms import DeviceForm
from .forms import BasicPlanForm
from .forms import TimeForm
from .forms import TimePlanForm

from .models import Device
from .models import BasicPlan
from .models import WaterTime
from .models import TimePlan


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


class AddDevice(View):
    template_name = "courses/course_create.html"
    model = Device

    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        form = DeviceForm
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        # POST method
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            form = DeviceForm()
            print("safe")
        context = {"form": form}

        return redirect('/gadget_communicator_pull/create')


class ListDevice(View):
    template_name = "courses/course_list.html"

    def get_queryset(self):
        return Device.objects.all()

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        return render(request, self.template_name, context)


class DeviceMixin(object):
    model = Device

    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj


class GetDeviceView(DeviceMixin, View):
    template_name = "courses/course_get.html"
    model = Device

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)



class DeviceDeleteView(DeviceMixin, View):
    template_name = "courses/course_delete.html"  # DetailView

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            context['object'] = obj
        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            obj.delete()
            context['object'] = None
            return redirect('/gadget_communicator_pull/list')
        return render(request, self.template_name, context)


class AddPlan(View):
    template_name = "courses/plan_create.html"
    model = BasicPlan

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        form = BasicPlanForm
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        # POST method
        form = BasicPlanForm(request.POST)
        if form.is_valid():
            form.save()
            form = BasicPlanForm()
            print("safe")
        context = {"form": form}

        return redirect('/gadget_communicator_pull/create')



class ListPlan(View):
    template_name = "courses/plan_list.html"

    def get_queryset(self):
        return BasicPlan.objects.all()

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        return render(request, self.template_name, context)


class TimeCreate(View):
    template_name = "courses/water_time_create.html"
    model = WaterTime

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        form = TimeForm
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        # POST method
        form = TimeForm(request.POST)
        if form.is_valid():
            print("safe1234")
            form.save()
            form = TimeForm()
            print("safe")
        else:
            print(form.errors)
        print("is not valid")
        context = {"form": form}

        return redirect('/gadget_communicator_pull/create_time_plan')


class AddPlanTime(View):
    template_name = "courses/time_plan_create.html"
    model = TimePlan

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        form = TimePlanForm
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        # POST method
        form = TimePlanForm(request.POST)
        if form.is_valid():
            form.save()
            form = TimePlanForm()
            print("safe")
        context = {"form": form}

        return redirect('/gadget_communicator_pull/create')

def hello_view(*args, **kwargs):
    return JsonResponse({'foo': 'bar'})
