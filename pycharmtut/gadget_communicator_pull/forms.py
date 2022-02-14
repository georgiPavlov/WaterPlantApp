from django import forms

from .models import BasicPlan
from .models import MoisturePlan
from .models import TimePlan
from .models import WaterTime
from .models import Device

WATER_PLAN_BASIC = 'basic'
WATER_PLAN_TIME = 'time_based'
WATER_PLAN_MOISTURE = 'moisture'


class DeviceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Device
        fields = [
            'device_id',
            'label'
        ]


class BasicPlanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BasicPlanForm, self).__init__(*args, **kwargs)
        self.fields['plan_type'].disabled = True
        self.fields['plan_type'].initial = WATER_PLAN_BASIC

    class Meta:
        model = BasicPlan
        fields = [
            'name',
            'plan_type',
            'water_volume',
        ]


class MoisturePlanForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MoisturePlanForm, self).__init__(*args, **kwargs)
        self.fields['plan_type'].disabled = True
        self.fields['plan_type'].initial = WATER_PLAN_MOISTURE

    class Meta:
        model = MoisturePlan
        fields = [
            'moisture_threshold',
            'check_interval',
        ]


class TimeForm(forms.ModelForm):
    class Meta:
        model = WaterTime
        fields = ['weekday', 'time_water']


class TimePlanForm(forms.ModelForm):
    time_plan_relation = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),
                                                        queryset=WaterTime.objects.all())

    def __init__(self, *args, **kwargs):
        super(TimePlanForm, self).__init__(*args, **kwargs)
        self.fields['plan_type'].disabled = True
        self.fields['plan_type'].initial = WATER_PLAN_TIME

    class Meta:
        model = TimePlan
        fields = ['time_plan_relation', ]



