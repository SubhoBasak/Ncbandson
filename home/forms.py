from django import forms
from . import models


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = models.ContactUs
        fields = ['name', 'email', 'subject', 'query']