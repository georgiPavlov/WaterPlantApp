from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from gadget_communicator_pull.forms.device_form import DeviceForm
from gadget_communicator_pull.models.device_module import Device


class AddDevice(View):
    template_name = "water/device_create.html"
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
    template_name = "water/device_list.html"

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
    template_name = "water/device_get.html"
    model = Device

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class DeviceDeleteView(DeviceMixin, View):
    template_name = "water/device_delete.html"  # DetailView

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
