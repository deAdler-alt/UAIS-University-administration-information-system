# management/urls.py
from django.urls import path
# Zaimportuj wszystkie potrzebne widoki, w tym nowe dla Osoba
from .views import (
    UserListView, UserCreateView, UserUpdateView, UserDeleteView,
    LogEntryListView, load_rady_dyscypliny,
    SkladRDListView, SkladRDCreateView, SkladRDUpdateView, SkladRDDeleteView,
    OsobaListView, OsobaCreateView, OsobaUpdateView, OsobaDeleteView # NOWE WIDOKI dla Osoba
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

    # --- Zarządzanie Osobami (NOWE) ---
    # Lista osób (z wyszukiwaniem)
    path('persons/', OsobaListView.as_view(), name='osoba_list'),
    # Dodawanie nowej osoby
    path('persons/add/', OsobaCreateView.as_view(), name='osoba_add'),
    # Edycja konkretnej osoby (identyfikowanej przez PK)
    path('persons/<int:pk>/edit/', OsobaUpdateView.as_view(), name='osoba_update'),
    # Usuwanie konkretnej osoby
    path('persons/<int:pk>/delete/', OsobaDeleteView.as_view(), name='osoba_delete'),
]