# management/urls.py
from django.urls import path
# Zaimportuj wszystkie potrzebne widoki, w tym nowe dla SkladRD
from .views import (
    UserListView, UserCreateView, UserUpdateView, UserDeleteView,
    LogEntryListView, load_rady_dyscypliny,
    SkladRDListView, SkladRDCreateView, SkladRDUpdateView, SkladRDDeleteView # NOWE WIDOKI dla SkladRD
)

app_name = 'management'

urlpatterns = [
    # --- Zarządzanie Użytkownikami ---
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # --- Dziennik Zdarzeń ---
    path('logs/', LogEntryListView.as_view(), name='log_entry_list'),

    # --- AJAX ---
    path('ajax/load-rady-dyscypliny/', load_rady_dyscypliny, name='ajax_load_rady_dyscypliny'),

    # --- Zarządzanie Składami Rad Dyscyplin (NOWE) ---
    # Lista wszystkich członków wszystkich rad (z opcją filtrowania)
    path('council-members/', SkladRDListView.as_view(), name='skladrd_list'),
    # Dodawanie nowego członka (ogólne, radę wybiera się w formularzu)
    path('council-members/add/', SkladRDCreateView.as_view(), name='skladrd_add'),
    # Edycja konkretnego wpisu członkostwa (identyfikowanego przez PK rekordu SkladRD)
    path('council-members/<int:pk>/edit/', SkladRDUpdateView.as_view(), name='skladrd_update'),
    # Usuwanie konkretnego wpisu członkostwa
    path('council-members/<int:pk>/delete/', SkladRDDeleteView.as_view(), name='skladrd_delete'),
]