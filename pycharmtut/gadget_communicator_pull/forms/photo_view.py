from django import forms

from gadget_communicator_pull.models.photo_module import PhotoModule


class PhotoForm(forms.ModelForm):

    class Meta:
        model = PhotoModule
        fields = ['image_dir']