from django import forms


class ProfileForm(forms.Form):
    name = forms.CharField(max_length=200, help_text="Enter your name")
    netid = forms.CharField(max_length=20, help_text="Enter your netid")
    phone = forms.CharField(max_length=20, help_text="Enter you phone")
    course = forms.CharField(max_length=200, help_text="Enter you course")
    food = forms.CharField(max_length=200, help_text="Enter you food")
    interest = forms.CharField(max_length=200, help_text="Enter you interest")

class LocationForm(forms.Form):
    longitude = forms.FloatField()
    latitude = forms.FloatField()

class SearchLocationForm(forms.Form):
    name = forms.CharField(max_length=200, help_text="Enter location name")
    locationType = forms.CharField(max_length=20, help_text="Enter location type")
    distanceLimit = forms.FloatField()
