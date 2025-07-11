"""
URL configuration for uais_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# uais_config/urls.py
from django.contrib import admin
from django.urls import path, include # Upewnij się, że include jest zaimportowane
from users import views as user_views
from django.http import HttpResponsePermanentRedirect

urlpatterns = [
    path('admin/', admin.site.urls), # Standardowy admin Django
    path('accounts/', include('users.urls')), # Logowanie/Wylogowanie lokalne 
    # path('accounts/', include('django_cas_ng.urls')), # Logowanie CAS (potem)
    path('', user_views.home_view, name='home'),

    # Nowa ścieżka do panelu zarządzania w aplikacji
    path('manage/', include('management.urls', namespace='management')),
    
    # Dodaj przekierowanie dla 127.0.0.1
    path('', lambda request: HttpResponsePermanentRedirect('/accounts/login') if request.get_host() == '127.0.0.1:8000' else None),
]