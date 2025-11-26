from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_student/', views.add_student, name='add_student'),
    path('issue_bus_pass/', views.issue_bus_pass, name='issue_bus_pass'),
    path('bus_routes/', views.bus_routes, name='bus_routes'),
    path('add_route/', views.add_route, name='add_route'),
    path('download_pass/<int:student_id>/', views.download_bus_pass, name='download_pass'),
]

