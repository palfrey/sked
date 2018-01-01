from django import forms

class NewCalendarForm(forms.Form):
    calendar_url = forms.URLField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Calendar URL'}))