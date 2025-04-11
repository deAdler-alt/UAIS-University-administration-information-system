from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    # Dodajemy 'rada_wydzialu' do listy wyświetlanych kolumn
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'role', 'rada_wydzialu')
    # Dodajemy 'rada_wydzialu' do filtrów
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role', 'rada_wydzialu')

    # Dodajemy 'rada_wydzialu' do sekcji pól w formularzu edycji
    # Kopiujemy fieldsets z BaseUserAdmin i modyfikujemy/dodajemy
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
         # Dodajemy nasze pola do jednej sekcji
        (_('Custom Fields'), {'fields': ('role', 'rada_wydzialu',)}),
    )

    # Dodajemy 'rada_wydzialu' do sekcji pól w formularzu dodawania
    # BaseUserAdmin.add_fieldsets zawiera już 'username', 'password', etc.
    # Sprawdzamy czy pola już tam nie ma dla pewności (choć nie powinno być)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Custom Fields'), {'fields': ('role', 'rada_wydzialu',)}),
    )

    # Definiujemy pola wyszukiwania
    search_fields = ('email', 'username', 'first_name', 'last_name')
    # Definiujemy kolejność
    ordering = ('email',)

# Rejestrujemy model User z naszą klasą UserAdmin
admin.site.register(User, UserAdmin)