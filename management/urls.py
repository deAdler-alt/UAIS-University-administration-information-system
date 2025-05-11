# management/urls.py
from django.urls import path
# Zaimportuj wszystkie potrzebne widoki
from .views import (
    UserListView, UserCreateView, UserUpdateView, UserDeleteView,
    LogEntryListView, load_rady_dyscypliny,
    SkladRDListView, SkladRDCreateView, SkladRDUpdateView, SkladRDDeleteView,
    OsobaListView, OsobaCreateView, OsobaUpdateView, OsobaDeleteView,
    # UWAGA: Dodajemy importy dla widoków Doktorant (które zaraz stworzymy)
    DoktorantListView, DoktorantCreateView, DoktorantUpdateView, DoktorantDeleteView
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

    # --- Zarządzanie Składami Rad Dyscyplin ---
    path('council-members/', SkladRDListView.as_view(), name='skladrd_list'),
    path('council-members/add/', SkladRDCreateView.as_view(), name='skladrd_add'),
    path('council-members/<int:pk>/edit/', SkladRDUpdateView.as_view(), name='skladrd_update'),
    path('council-members/<int:pk>/delete/', SkladRDDeleteView.as_view(), name='skladrd_delete'),

    # --- Zarządzanie Osobami ---
    path('persons/', OsobaListView.as_view(), name='osoba_list'),
    path('persons/add/', OsobaCreateView.as_view(), name='osoba_add'),
    path('persons/<int:pk>/edit/', OsobaUpdateView.as_view(), name='osoba_update'),
    path('persons/<int:pk>/delete/', OsobaDeleteView.as_view(), name='osoba_delete'),

    # --- Zarządzanie Doktorantami (NOWE) ---
    # UWAGA: Dodano nowe ścieżki URL dla modelu Doktorant
    path('doktoranci/', DoktorantListView.as_view(), name='doktorant_list'),
    path('doktoranci/add/', DoktorantCreateView.as_view(), name='doktorant_add'),
    path('doktoranci/<int:pk>/edit/', DoktorantUpdateView.as_view(), name='doktorant_update'),
    path('doktoranci/<int:pk>/delete/', DoktorantDeleteView.as_view(), name='doktorant_delete'),
]