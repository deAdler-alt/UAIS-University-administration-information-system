# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Importujemy bazowy UserAdmin
from .models import User # Importujemy nasz model User

# Możemy rozszerzyć domyślny UserAdmin, aby dodać pole 'role'
class UserAdmin(BaseUserAdmin):
    # Pola wyświetlane na liście użytkowników w panelu admina
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role') # Dodajemy 'role'
    # Filtry dostępne po prawej stronie listy
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role') # Dodajemy 'role'

    # Definicja sekcji (fieldsets) w formularzu edycji użytkownika
    # Kopiujemy domyślne fieldsets z BaseUserAdmin i dodajemy nasze pole 'role'
    # Możesz sprawdzić domyślne fieldsets w kodzie źródłowym Django lub dokumentacji
    fieldsets = (
        (None, {'fields': ('username', 'password')}), # Sekcja logowania
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}), # Dane osobowe
        ('Permissions', { # Uprawnienia
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}), # Daty
        ('Custom Fields', {'fields': ('role',)}), # NASZA SEKCJA Z ROLĄ
    )

    # Można też użyć add_fieldsets, jeśli dziedziczymy i chcemy tylko dodać sekcję
    # add_fieldsets = (
    #     ('Custom Fields', {'fields': ('role',)}),
    # )

    # Pola dostępne do edycji w formularzu dodawania użytkownika
    # Kopiujemy z BaseUserAdmin i dodajemy 'role'
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

    # Pola tylko do odczytu
    # readonly_fields = ('last_login', 'date_joined') # Są już w BaseUserAdmin


# Rejestrujemy nasz model User z niestandardową klasą UserAdmin
admin.site.register(User, UserAdmin)