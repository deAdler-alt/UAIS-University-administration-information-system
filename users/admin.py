# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
# Dodano SkladRD do importów
from .models import User, Wydzial, RadaDyscypliny, LogEntry, Funkcja_czlonka, Osoba, SkladRD, Adres, Adres_Osoba, Uprawnienia

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'role', 'wydzial', 'rada_dyscypliny_fk')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role', 'wydzial')
    fieldsets = (
        (None, {'fields': ('password',)}),
        (_('Personal info'), {'fields': ('email', 'first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Custom Fields'), {'fields': ('role', 'wydzial', 'rada_dyscypliny_fk',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password', 'password2')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Custom Fields'), {'fields': ('role', 'wydzial', 'rada_dyscypliny_fk',)}),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# Rejestrujemy model User z naszą klasą UserAdmin
admin.site.register(User, UserAdmin)

# --- Rejestracja pozostałych modeli ---

@admin.register(Wydzial)
class WydzialAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)

@admin.register(RadaDyscypliny)
class RadaDyscyplinyAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'wydzial')
    list_filter = ('wydzial',)
    search_fields = ('nazwa', 'wydzial__nazwa')
    autocomplete_fields = ['wydzial']

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_display_name', 'action_type', 'details_preview', 'ip_address')
    list_filter = ('action_type', 'timestamp', 'user')
    search_fields = ('user__email', 'details', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action_type', 'details', 'ip_address')
    date_hierarchy = 'timestamp'

    @admin.display(description='Użytkownik')
    def user_display_name(self, obj):
        return str(obj.user) if obj.user else "System"

    @admin.display(description='Szczegóły (podgląd)')
    def details_preview(self, obj):
        return (obj.details[:75] + '...') if obj.details and len(obj.details) > 75 else obj.details

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

# Rejestracja modeli pomocniczych (jeśli chcemy nimi zarządzać w adminie)
@admin.register(Funkcja_czlonka)
class FunkcjaCzlonkaAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)

@admin.register(Uprawnienia)
class UprawnieniaAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)

@admin.register(Adres)
class AdresAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'miasto', 'kod_pocztowy', 'ulica', 'nr_budynku', 'afiliacja_uczelnia')
    search_fields = ('miasto', 'ulica', 'kod_pocztowy', 'afiliacja_uczelnia', 'afiliacja_wydzial', 'afiliacja_jednostka')
    list_filter = ('miasto', 'afiliacja_uczelnia')

# Inline dla Adres_Osoba (aby zarządzać adresami z poziomu Osoby)
class AdresOsobaInline(admin.TabularInline):
    model = Adres_Osoba
    extra = 1 # Ile pustych formularzy powiązania adresu dodać na stronie Osoby
    autocomplete_fields = ['adres'] # Ułatwia wybór adresu

@admin.register(Osoba)
class OsobaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'stanowisko', 'plec')
    search_fields = ('imie', 'nazwisko', 'email', 'tytul_stopien', 'stanowisko', 'specjalnosci')
    list_filter = ('plec', 'tytul_stopien', 'stanowisko')
    # Pola do odmian mogą być duże, więc umieszczamy je w sekcjach
    fieldsets = (
        (None, {'fields': ('imie', 'nazwisko', 'plec')}),
        ('Dane kontaktowe i zawodowe', {'fields': ('email', 'telefon', 'tytul_stopien', 'tytul_po', 'stanowisko', 'specjalnosci', 'link_do_profilu_nauka_polska')}),
        ('Odmiana (dopełniacz)', {'fields': ('imie_nazwisko_dopelniacz',)}),
        ('Odmiana (celownik)', {'fields': ('imie_nazwisko_celownik',)}),
        ('Odmiana (biernik)', {'fields': ('imie_nazwisko_biernik',)}),
    )
    inlines = [AdresOsobaInline] # Dodajemy możliwość zarządzania adresami inline

# --- NOWA Rejestracja dla SkladRD ---
@admin.register(SkladRD)
class SkladRDAdmin(admin.ModelAdmin):
    list_display = ('osoba', 'funkcja_czlonka', 'rd', 'data_powolania', 'aktywny')
    list_filter = ('rd', 'funkcja_czlonka', 'aktywny')
    search_fields = ('osoba__imie', 'osoba__nazwisko', 'osoba__email', 'rd__nazwa')
    autocomplete_fields = ['rd', 'osoba', 'funkcja_czlonka'] # Ułatwia wybór powiązanych obiektów
    date_hierarchy = 'data_powolania' # Dodaje nawigację po dacie