from django.contrib import admin
from django.urls import path, include
from users.views import home  # Dodajemy nasz widok

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),  # Strona główna
]