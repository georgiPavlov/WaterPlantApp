from django import forms
from gadget_communicator_pull.models.basic_plan_module import BasicPlan
from gadget_communicator_pull.models.device_module import Device

WATER_PLAN_BASIC = 'basic'



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
