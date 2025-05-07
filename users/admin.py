from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Wydzial, RadaDyscypliny, LogEntry # Dodano importy nowych modeli

class UserAdmin(BaseUserAdmin):
    # Zaktualizowana lista wyświetlanych kolumn
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'role', 'wydzial', 'rada_dyscypliny_fk')
    # Zaktualizowane filtry
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role', 'wydzial')

    # Zaktualizowane sekcje pól w formularzu edycji
    # Usuwamy 'username' i zamieniamy 'rada_wydzialu'
    fieldsets = (
        # (None, {'fields': ('username', 'password')}), # Usunięto username
        (None, {'fields': ('password',)}), # Pozostaje tylko hasło, email jest w Personal info
        (_('Personal info'), {'fields': ('email', 'first_name', 'last_name')}), # Dodano email tutaj, bo jest głównym identyfikatorem
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        # Zaktualizowane pola niestandardowe
        (_('Custom Fields'), {'fields': ('role', 'wydzial', 'rada_dyscypliny_fk',)}),
    )

    # Zaktualizowane sekcje pól w formularzu dodawania
    # Rekonstrukcja add_fieldsets, aby usunąć 'username' i dodać nasze pola
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Pole 'username' jest domyślnie wymagane przez BaseUserAdmin, ale my go nie używamy
            # Zamiast tego, email jest naszym USERNAME_FIELD
            'fields': ('email', 'password', 'password2'), # password2 dla potwierdzenia
        }),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Custom Fields'), {'fields': ('role', 'wydzial', 'rada_dyscypliny_fk',)}),
    )
    # Uwaga: BaseUserAdmin.add_form domyślnie zawiera logikę dla username.
    # Przy USERNAME_FIELD='email', Django powinno sobie z tym poradzić, ale
    # warto przetestować dodawanie użytkownika przez panel admina.

    # Zaktualizowane pola wyszukiwania
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# Rejestrujemy model User z naszą klasą UserAdmin
admin.site.register(User, UserAdmin)

# Rejestracja nowych modeli w panelu admina
@admin.register(Wydzial)
class WydzialAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)

@admin.register(RadaDyscypliny)
class RadaDyscyplinyAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'wydzial')
    list_filter = ('wydzial',)
    search_fields = ('nazwa', 'wydzial__nazwa')
    autocomplete_fields = ['wydzial'] # Ułatwia wybór wydziału

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_display_name', 'action_type', 'details_preview', 'ip_address')
    list_filter = ('action_type', 'timestamp', 'user')
    search_fields = ('user__email', 'details', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action_type', 'details', 'ip_address') # Logi tylko do odczytu
    date_hierarchy = 'timestamp'

    def user_display_name(self, obj):
        return str(obj.user) if obj.user else "System"
    user_display_name.short_description = 'Użytkownik'

    def details_preview(self, obj):
        return (obj.details[:75] + '...') if obj.details and len(obj.details) > 75 else obj.details
    details_preview.short_description = 'Szczegóły (podgląd)'

    # Aby uniknąć możliwości dodawania/zmiany logów z panelu admina
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False # Można ustawić na True, jeśli chcemy pozwolić na edycję, ale to rzadkie dla logów

    # def has_delete_permission(self, request, obj=None): # Domyślnie True, można ustawić na False
    #     return False