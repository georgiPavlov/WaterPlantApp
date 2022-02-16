from datetime import datetime

from django import forms
from django.forms import DateField

from . import helper
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
    relation = forms.ModelChoiceField(queryset=Device.objects.all())

    def __init__(self, *args, **kwargs):
        super(BasicPlanForm, self).__init__(*args, **kwargs)
        self.fields['plan_type'].disabled = True
        self.fields['plan_type'].initial = WATER_PLAN_BASIC

    def save(self, commit=True):
        instance = super(BasicPlanForm, self).save(commit=False)
        pub = self.cleaned_data['relation']
        print(type(pub))
        print(type(instance))
        instance.device_relation = pub
        instance.save(commit)
        return instance

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
    time_rel = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))


    class Meta:
        model = WaterTime
        fields = ['weekday', 'time_rel']

    def save(self, commit=True):
        instance = super(TimeForm, self).save(commit=False)
        time_rel = self.cleaned_data['time_rel']

        instance.time_water = str(time_rel)
        instance.save(commit)
        return instance


class TimePlanForm(forms.ModelForm):
    water_time_rel = forms.ModelChoiceField(queryset=WaterTime.objects.all())
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
        instance.water_time_relation = water_time_rel
        instance.save(commit)
        return instance
