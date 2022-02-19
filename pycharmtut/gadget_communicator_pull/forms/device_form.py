from django import forms
from gadget_communicator_pull.models.device_module import Device


class DeviceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Device
        fields = [
            'device_id',
            'label'
        ]
