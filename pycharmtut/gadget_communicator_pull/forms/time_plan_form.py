from django import forms
from gadget_communicator_pull.models.time_plan_module import TimePlan
from gadget_communicator_pull.models.water_time_module import WaterTime
from gadget_communicator_pull.models.device_module import Device

WATER_PLAN_TIME = 'time_based'


class TimePlanForm(forms.ModelForm):
    water_time_rel = forms.ModelMultipleChoiceField(queryset=WaterTime.objects.all())
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
        instance.device_relation = device_rel
        instance.save(commit)
        for i in water_time_rel:
            instance.water_time_relation.add(i)
        return instance
