# users/admin.py (POPRAWIONA WERSJA)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
# Importujemy NOWY model User i Uprawnienia
from .models import User, Uprawnienia
# Importujemy Osoba, RD dla celów wyświetlania/filtrowania
from core.models import Osoba, RD

# Rejestrujemy prosty model Uprawnienia
@admin.register(Uprawnienia)
class UprawnieniaAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)

# Definiujemy nowy UserAdmin dla nowego modelu User
@admin.register(User) # Używamy dekoratora do rejestracji
class UserAdmin(BaseUserAdmin):
    # --- Pola używane przez BaseUserAdmin, które musimy dostosować ---
    ordering = ('email',) # Sortowanie po emailu
    list_display = ('email', 'get_full_name_from_osoba', 'uprawnienia', 'rd', 'aktywny', 'is_staff') # Używamy nowych pól i metody
    list_filter = ('aktywny', 'is_staff', 'is_superuser', 'uprawnienia', 'rd', 'groups') # Używamy nowych pól (aktywny zamiast is_active, uprawnienia, rd)
    search_fields = ('email', 'osoba__imie', 'osoba__nazwisko') # Szukamy po emailu lub imieniu/nazwisku w powiązanej Osobie
    readonly_fields = ('last_login', 'date_joined') # Pola tylko do odczytu

    # --- Definicja sekcji w formularzu edycji ---
    # Musimy całkowicie przedefiniować fieldsets, bo BaseUserAdmin używa starych pól
    fieldsets = (
        # Sekcja 1: Dane logowania i status
        (None, {'fields': ('email', 'password')}), # Hasło jest specjalnie obsługiwane przez BaseUserAdmin
        (_('Status'), {'fields': ('aktywny', 'is_staff', 'is_superuser')}),
        # Sekcja 2: Nasze powiązania
        (_('Powiązania UAIS'), {'fields': ('uprawnienia', 'rd', 'osoba')}),
        # Sekcja 3: Uprawnienia Django (jeśli używamy PermissionsMixin)
        (_('Uprawnienia Django'), {'fields': ('groups', 'user_permissions')}),
        # Sekcja 4: Ważne daty
        (_('Ważne daty'), {'fields': ('last_login', 'date_joined')}),
    )

    # --- Definicja pól w formularzu DODAWANIA użytkownika ---
    # BaseUserAdmin ma własny add_form i add_fieldsets, musimy je dostosować
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'), # Standardowe pola formularza dodawania z BaseUserAdmin (password2 do potwierdzenia)
        }),
         # Sekcja 2: Nasze powiązania (możemy wymagać przy tworzeniu?)
        (_('Powiązania UAIS'), {'fields': ('uprawnienia', 'rd', 'osoba')}),
         # Sekcja 3: Uprawnienia Django
         (_('Uprawnienia Django'), {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
         # Dodajemy pole 'aktywny'
         (_('Status'), {'fields': ('aktywny',)}),
    )
    # Musimy też dostarczyć formularz dodawania, który obsłuży password2
    # Możemy użyć wbudowanego UserCreationForm lub stworzyć własny
    # Na razie zostawiamy domyślny z BaseUserAdmin - może wymagać dostosowania później

    # --- Metody pomocnicze do wyświetlania danych z powiązanych modeli ---
    @admin.display(description=_('Imię i Nazwisko (z Osoba)'))
    def get_full_name_from_osoba(self, obj):
        if obj.osoba:
            return obj.osoba.get_full_name()
        return "-" # Lub obj.email jeśli osoba nie jest powiązana

    # Można dodać więcej metod, np. get_uprawnienia_nazwa, get_rd_nazwa

# Uwaga: Standardowa rejestracja admin.site.register(User, UserAdmin) jest zastąpiona
# przez dekorator @admin.register(User) nad definicją klasy.