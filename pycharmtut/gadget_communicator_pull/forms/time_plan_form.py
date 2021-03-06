from django import forms

from gadget_communicator_pull.constants.water_constants import WATER_PLAN_TIME
from gadget_communicator_pull.models.time_plan_module import TimePlan
from gadget_communicator_pull.models.water_time_module import WaterTime
from gadget_communicator_pull.models.device_module import Device


class TimePlanForm(forms.ModelForm):
    water_time_rel = forms.ModelMultipleChoiceField(queryset=WaterTime.objects.filter(is_in_use=False))
    relation_rel = forms.ModelChoiceField(queryset=Device.objects.all())

    def __init__(self, *args, **kwargs):
        super(TimePlanForm, self).__init__(*args, **kwargs)
        self.fields['plan_type'].disabled = True
        self.fields['plan_type'].initial = WATER_PLAN_TIME

    class Meta:
        model = TimePlan
        fields = ['relation_rel',
                  'water_time_rel',
                  'name',
                  'plan_type',
                  'water_volume',
                  ]

    def save(self, commit=True):
        instance = super(TimePlanForm, self).save(commit=False)
        device_rel = self.cleaned_data['relation_rel']
        water_time_rel = self.cleaned_data['water_time_rel']

        instance.save(commit)
        instance.devices_t.add(device_rel)

        for i in water_time_rel:
            i.is_in_use = True
            i.save()
            instance.water_times.add(i)
        return instance
