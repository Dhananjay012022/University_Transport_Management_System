from django import forms
from .models import Student, BusPass, BusRoute
from .models import BusRoute

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'email', 'bus_route']

class BusPassForm(forms.ModelForm):
    class Meta:
        model = BusPass
        fields = ['student', 'expiry_date', 'pass_number']

class BusRouteForm(forms.ModelForm):
    class Meta:
        model = BusRoute
        fields = ['route_name', 'start_location', 'end_location', 'driver_name', 'capacity']