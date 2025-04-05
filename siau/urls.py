from django.contrib import admin
from django.urls import path, include
from users.views import (custom_login, manage_users, legal_docs, add_doc,
                         archive_docs, edit_user, delete_user, dashboard,
                         catalog, for_everyone)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', custom_login, name='login'),
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard'),
    path('catalog/', catalog, name='catalog'),
    path('for_everyone/', for_everyone, name='for_everyone'),
    path('manage_users/', manage_users, name='manage_users'),
    path('edit_user/<int:user_id>/', edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
    path('legal_docs/', legal_docs, name='legal_docs'),
    path('add_doc/', add_doc, name='add_doc'),
    path('archive_docs/', archive_docs, name='archive_docs'),
]