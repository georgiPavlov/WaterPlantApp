import json as simplejson
from django.core import serializers

from django.shortcuts import render, redirect
from django.views import View
from gadget_communicator_pull.forms.basic_plan_form import BasicPlanForm
from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.basic_plan_module import BasicPlan
from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer





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
            print("valid")
        context = {"form": form}

        return redirect('/gadget_communicator_pull/create')


class ListPlan(View):
    template_name = "courses/plan_list.html"

    def get_queryset(self):
        return BasicPlan.objects.all()

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        for f in BasicPlan.objects.all():
            print(f)
        basicPlan = BasicPlan.objects.all()[0]
        print(f"id {basicPlan.id}")
        print(type(basicPlan.devices_b))
        print(type(Device.objects.all().first().device_relation_b))
        print(f"id {basicPlan.id}")
        for c in Device.objects.all():
            print(c)
            print(c.device_relation_b)
        devices = Device.objects.filter(device_relation_b=basicPlan)
        print(type(devices.first()))
        print(f'label2 {devices.first().label}')
        #print(f"label:  {devices.first().label}")
        print("213")
        for i in BasicPlan.objects.all():
            serializer = BasePlanSerializer(instance=i)
            print(serializer.data)
            payload = simplejson.loads(simplejson.dumps(serializer.data))
            print(payload)


        # serialized_obj = serializers.serialize('json', [basicPlan, ],indent = 4, relations = ('object_type', 'individual',)))
        #serialized_obj = serializer.serialize("json", [basicPlan], indent=4, relations = ('device_relation',))





        return render(request, self.template_name, context)
