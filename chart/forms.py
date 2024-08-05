from django import forms
from .models import SaveDetail


class SaveDetailForm(forms.ModelForm):
    class Meta:
        model = SaveDetail
        fields = ['text']
