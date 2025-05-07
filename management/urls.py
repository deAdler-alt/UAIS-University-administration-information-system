# management/urls.py
from django.urls import path
# Zaimportuj nowe widoki
from .views import (
    UserListView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
    LogEntryListView,       # NOWY WIDOK
    load_rady_dyscypliny    # NOWY WIDOK (funkcja)
)

app_name = 'management'

urlpatterns = [
    # Istniejące ścieżki dla zarządzania użytkownikami
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # NOWA ŚCIEŻKA dla Dziennika Zdarzeń
    path('logs/', LogEntryListView.as_view(), name='log_entry_list'),

    # NOWA ŚCIEŻKA dla AJAX do ładowania Rad Dyscypliny
    path('ajax/load-rady-dyscypliny/', load_rady_dyscypliny, name='ajax_load_rady_dyscypliny'),
]