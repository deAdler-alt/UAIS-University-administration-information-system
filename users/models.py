# users/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
# Importujemy modele z aplikacji core
# WAŻNE: Django musi być w stanie zaimportować te modele,
# upewnij się, że aplikacja 'core' jest przed 'users' w INSTALLED_APPS

class Uprawnienia(models.Model):
    # Wewnętrzne wartości ról - do użycia w kodzie
    ADMIN = 'ADMIN'
    PRAWNIK = 'PRAWNIK'
    POMOC = 'POMOC' # Zamiast OBSLUGA
    RADA_ZARZAD = 'RADA_ZARZAD'
    # Można dodać inne z komentarza SQL, jeśli potrzebne
    # PRZEWODNICZACY = 'PRZEWODNICZACY'
    # WICEPRZEWODNICZACY = 'WICEPRZEWODNICZACY'
    # SEKRETARZ = 'SEKRETARZ'

    # Można zdefiniować CHOICES dla pola 'nazwa', jeśli chcemy ograniczyć
    ROLE_CHOICES = [
        (ADMIN, _('Administrator')),
        (PRAWNIK, _('Radca prawny')),
        (POMOC, _('Pomoc administracyjna')),
        (RADA_ZARZAD, _('Zarząd Rady Dyscypliny')),
        # Można dodać inne
    ]
    # Uwaga: Pole 'nazwa' przechowuje np. 'ADMIN', 'PRAWNIK' itd.
    nazwa = models.CharField(
        _("Nazwa uprawnienia"),
        max_length=50, # Krótsza długość wystarczy na identyfikatory
        unique=True,
        choices=ROLE_CHOICES # Ograniczamy wybór w panelu admina/formularzach
    )

    class Meta:
        verbose_name = _("Uprawnienie")
        verbose_name_plural = _("Uprawnienia")
        ordering = ['nazwa']

    def __str__(self):
        return self.get_nazwa_display() # Zwraca czytelną nazwę z choices

class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Tworzy i zapisuje użytkownika z hashowanym hasłem."""
        if not email:
            raise ValueError('Podany email musi być ustawiony')
        email = self.normalize_email(email)
        # Powiązanie z Osoba - zakładamy, że Osoba jest tworzona osobno
        # lub że 'osoba_id' jest przekazane w extra_fields
        # user = self.model(email=email, is_staff=is_staff, is_active=True, # Domyślnie is_active=True
        #                  is_superuser=is_superuser, **extra_fields)

        # Poprawka: Tworzymy usera BEZ osoby na razie, dodamy ją później lub przekażemy
        # Usuwamy też 'imie', 'nazwisko' stąd, bo są w Osoba
        user = self.model(email=email, is_staff=is_staff, aktywny=True,
                         is_superuser=is_superuser, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        # Tworzy zwykłego użytkownika
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        # Tworzy superużytkownika
        # Zapewniamy, że superuser ma odpowiednie flagi
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superużytkownik musi mieć is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superużytkownik musi mieć is_superuser=True.')

        # Przypisujemy uprawnienie ADMIN dla superusera
        try:
            admin_uprawnienie = Uprawnienia.objects.get(nazwa=Uprawnienia.ADMIN)
            extra_fields['uprawnienia'] = admin_uprawnienie
        except Uprawnienia.DoesNotExist:
            # Jeśli uprawnienie ADMIN nie istnieje, logujemy ostrzeżenie lub tworzymy je
            print("OSTRZEŻENIE: Uprawnienie ADMIN nie istnieje w bazie danych!")
            # admin_uprawnienie = Uprawnienia.objects.create(nazwa=Uprawnienia.ADMIN)
            # extra_fields['uprawnienia'] = admin_uprawnienie

        # Tworzymy superużytkownika używając _create_user
        # Usuwamy 'imie' i 'nazwisko' z wymaganych dla _create_user, bo są w Osoba
        # Będziemy musieli je podać przy tworzeniu obiektu Osoba
        return self._create_user(email, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Niestandardowy model użytkownika dla UAIS v2"""
    email = models.EmailField(_('Email (login)'), unique=True, max_length=255)
    # Usuwamy imie i nazwisko - będą w powiązanym modelu Osoba
    # imie = models.CharField(_('Imię'), max_length=255)
    # nazwisko = models.CharField(_('Nazwisko'), max_length=255)
    aktywny = models.BooleanField(_('Aktywny'), default=True) # Odpowiada polu is_active z AbstractBaseUser
    is_staff = models.BooleanField(_('Dostęp do admina Django'), default=False) # Dla /admin/

    # Nasze specyficzne powiązania
    # PROTECT: Nie można usunąć uprawnienia/rady, jeśli user jest przypisany
    # null=True, blank=True: Użytkownik nie musi mieć od razu przypisanych uprawnień/rady
    uprawnienia = models.ForeignKey(Uprawnienia, verbose_name=_("Uprawnienia"), on_delete=models.PROTECT, null=True, blank=True, related_name='uzytkownicy')
    rd = models.ForeignKey('core.RD', verbose_name=_("Rada Dyscypliny"), on_delete=models.SET_NULL, null=True, blank=True, related_name='uzytkownicy') # Używamy stringa 'core.RD'

    # Relacja 1-do-1 z modelem Osoba (zdefiniowanym w core.models)
    # CASCADE: Usunięcie User kasuje powiązaną Osobę. Można zmienić na PROTECT/SET_NULL.
    # null=True: Pozwalamy na User bez Osoba (np. tymczasowo przy tworzeniu)
    osoba = models.OneToOneField('core.Osoba', verbose_name=_("Dane Osobowe"), on_delete=models.CASCADE, related_name='konto_uzytkownika', null=True, blank=True)

    # Pole wymagane przez AbstractBaseUser
    date_joined = models.DateTimeField(_('Data dołączenia'), auto_now_add=True)

    # Ustawiamy własny Manager
    objects = UserManager()

    # Pole używane do logowania
    USERNAME_FIELD = 'email'
    # Pola wymagane przy tworzeniu użytkownika przez 'createsuperuser'
    # Oprócz email i hasła. Imię/Nazwisko są teraz w Osoba.
    REQUIRED_FIELDS = [] # Zmieniamy na pustą listę

    class Meta:
        verbose_name = _('Użytkownik Systemu')
        verbose_name_plural = _('Użytkownicy Systemu')

    def __str__(self):
        return self.email

    # Metody dla kompatybilności i wygody
    def get_full_name(self):
        if self.osoba:
            return f"{self.osoba.imie} {self.osoba.nazwisko}".strip()
        return self.email # Fallback

    def get_short_name(self):
        if self.osoba:
            return self.osoba.imie
        return self.email.split('@')[0] # Fallback

    @property
    def is_active(self):
        "Is the user active?"
        return self.aktywny

    # is_staff i is_superuser są już polami z PermissionsMixin