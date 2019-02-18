from django import forms
from django.core import validators

class URLCustomSchemes(forms.URLField):
    default_validators = []

class NewCalendarForm(forms.Form):
    calendar_url = URLCustomSchemes(
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Calendar URL'}),
        validators=[validators.URLValidator(schemes=["http", "https", "webcal"])])

class NewWhosoffCalendarForm(forms.Form):
    calendar_url = URLCustomSchemes(
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Calendar URL'}),
        validators=[validators.URLValidator(schemes=["http", "https", "webcal"])])
    person = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Exact name (as per Whosoff data) for the person you want to filter on'}))

class MergedCalendarForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Calendar name (possibly name of the person this will be shared with)'}))