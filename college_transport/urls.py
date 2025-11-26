from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main auth routes
    path('login/', auth_views.LoginView.as_view(template_name='transport/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Extra aliases so Django's default /accounts/login/ redirect also works
    path('accounts/login/', auth_views.LoginView.as_view(template_name='transport/login.html')),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login')),

    # App URLs
    path('', include('transport.urls')),
]
