from django.shortcuts import render, redirect
from django.views import View
from gadget_communicator_pull.forms.moisture_form import MoistureForm
from gadget_communicator_pull.models.moisture_plan_module import MoisturePlan


class AddMoistureTime(View):
    template_name = "courses/moisture_plan_create.html"
    model = MoisturePlan

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        form = MoistureForm
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        # POST method
        form = MoistureForm(request.POST)
        if form.is_valid():
            form.save()
            form = MoistureForm()
            print("safe")
        context = {"form": form}

        return redirect('/gadget_communicator_pull/create')
