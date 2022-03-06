from django import forms
from gadget_communicator_pull.models.water_time_module import WaterTime


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
