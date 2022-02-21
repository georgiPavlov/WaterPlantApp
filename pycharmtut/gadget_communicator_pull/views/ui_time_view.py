from django.shortcuts import render, redirect
from django.views import View
from gadget_communicator_pull.forms.time_form import TimeForm
from gadget_communicator_pull.models.water_time_module import WaterTime


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
            print("safe")
        else:
            print(form.errors)



        return redirect('/gadget_communicator_pull/create_time_plan')