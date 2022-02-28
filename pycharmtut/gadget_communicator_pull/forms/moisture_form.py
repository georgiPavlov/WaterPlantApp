from django import forms
from gadget_communicator_pull.models.moisture_plan_module import MoisturePlan
from gadget_communicator_pull.models.device_module import Device

WATER_PLAN_MOISTURE = 'moisture'


class MoistureForm(forms.ModelForm):
    relation_rel = forms.ModelChoiceField(queryset=Device.objects.all())

    def __init__(self, *args, **kwargs):
        super(MoistureForm, self).__init__(*args, **kwargs)
        self.fields['plan_type'].disabled = True
        self.fields['plan_type'].initial = WATER_PLAN_MOISTURE

    class Meta:
        model = MoisturePlan
        fields = ['relation_rel',
                  'name',
                  'plan_type',
                  'water_volume',
                  'moisture_threshold',
                  'check_interval',
                  ]

    def save(self, commit=True):
        instance = super(MoistureForm, self).save(commit=False)
        device_rel = self.cleaned_data['relation']
        instance.save(commit)
        instance.devices_m.add(device_rel)
        return instance
