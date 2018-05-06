from django import forms

class NewCalendarForm(forms.Form):
    calendar_url = forms.URLField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Calendar URL'}))

class MergedCalendarForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Calendar name (possibly name of the person this will be shared with)'}))