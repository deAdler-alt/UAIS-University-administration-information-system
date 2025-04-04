from django.contrib import admin
from django.urls import path, include
from users.views import home, no_role, admin_section, manage_users

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),
    path('no-role/', no_role, name='no_role'),
    path('admin_section/', admin_section, name='admin_section'),
    path('manage_users/', manage_users, name='manage_users'),
]