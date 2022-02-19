from django.shortcuts import render, redirect
from django.views import View
from gadget_communicator_pull.forms.time_plan_form import TimePlanForm
from gadget_communicator_pull.models.time_plan_module import TimePlan


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


class ListTimePlan(View):
    template_name = "courses/plan_time_list.html"

    def get_queryset(self):
        return TimePlan.objects.all()

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        return render(request, self.template_name, context)
