from django.contrib import admin
from .models import Student, BusPass, BusRoute

admin.site.register(Student)
admin.site.register(BusPass)
admin.site.register(BusRoute)
