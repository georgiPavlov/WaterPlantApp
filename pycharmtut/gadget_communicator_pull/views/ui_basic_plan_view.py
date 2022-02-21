import json as simplejson
from django.core import serializers

from django.shortcuts import render, redirect
from django.views import View
from gadget_communicator_pull.forms.basic_plan_form import BasicPlanForm
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
            print("safe")
        context = {"form": form}

        return redirect('/gadget_communicator_pull/create')


class ListPlan(View):
    template_name = "courses/plan_list.html"

    def get_queryset(self):
        return BasicPlan.objects.all()

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        basicPlan = BasicPlan.objects.all()[:1].get()
        print()
        serializer = BasePlanSerializer(instance=basicPlan)

        # serialized_obj = serializers.serialize('json', [basicPlan, ],indent = 4, relations = ('object_type', 'individual',)))
        #serialized_obj = serializer.serialize("json", [basicPlan], indent=4, relations = ('device_relation',))
        print(serializer.data)




        return render(request, self.template_name, context)
