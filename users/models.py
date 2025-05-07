#users/models.py
from django.conf import settings # Potrzebne dla LogEntry.user -> settings.AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nowy model Wydzial
class Wydzial(models.Model):
    nazwa = models.CharField(max_length=255, unique=True, verbose_name="Nazwa wydziału")

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = "Wydział"
        verbose_name_plural = "Wydziały"
        ordering = ['nazwa']

# Nowy model RadaDyscypliny
class RadaDyscypliny(models.Model):
    nazwa = models.CharField(max_length=255, verbose_name="Nazwa rady dyscypliny")
    wydzial = models.ForeignKey(Wydzial, on_delete=models.CASCADE, verbose_name="Wydział", related_name="rady_dyscypliny")

    def __str__(self):
        return f"{self.nazwa} ({self.wydzial.nazwa})"

    class Meta:
        verbose_name = "Rada Dyscypliny"
        verbose_name_plural = "Rady Dyscypliny"
        ordering = ['wydzial', 'nazwa']
        unique_together = ('nazwa', 'wydzial') # Nazwa rady musi być unikalna w obrębie wydziału

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        PRAWNIK = 'PRAWNIK', _('Radca prawny')
        OBSLUGA = 'OBSLUGA', _('Pomoc administracyjna')
        RADA = 'RADA', _('Zarząd Rady Dyscypliny')

    role = models.CharField(
        _('Rola'),
        max_length=50,
        choices=Role.choices,
        null=True,
        blank=True
    )

    # Stare pole rada_wydzialu - skomentowane, aby nie powodowało konfliktu.
    # Można je później usunąć całkowicie po upewnieniu się, że dane zostały zmigrowane
    # lub nie są już potrzebne w starej formie.
    # rada_wydzialu = models.CharField(
    #     _('Rada/Jednostka'),
    #     max_length=255,
    #     blank=True,
    #     default='Wydział Elektrotechniki i Informatyki' # Usuniemy to po migracji danych
    # )

    # Nowe pola ForeignKey
    wydzial = models.ForeignKey(
        Wydzial,
        on_delete=models.SET_NULL, # Umożliwia usunięcie wydziału bez usuwania użytkowników
        null=True,                 # Użytkownik może nie mieć przypisanego wydziału
        blank=True,                # Pole nie jest wymagane w formularzach
        verbose_name="Wydział"
    )
    rada_dyscypliny_fk = models.ForeignKey(
        RadaDyscypliny,
        on_delete=models.SET_NULL, # Umożliwia usunięcie rady bez usuwania użytkowników
        null=True,                 # Użytkownik może nie mieć przypisanej rady
        blank=True,                # Pole nie jest wymagane w formularzach
        verbose_name="Rada Dyscypliny"
    )

    # Zalecane, jeśli email ma być głównym identyfikatorem
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Usunięto 'username'

    # Pole username odziedziczone z AbstractUser nadal istnieje w bazie,
    # ale nie jest używane do logowania ani nie jest wymagane.
    # Można rozważyć nadpisanie go, aby było nieedytowalne lub miało inne właściwości,
    # ale na razie pozostawienie go bez zmian (poza usunięciem z REQUIRED_FIELDS)
    # powinno być wystarczające.
    # username = None # To spowoduje błąd, nie można usunąć pola w ten sposób

    def __str__(self):
        return self.email

# Nowy model LogEntry dla dziennika zdarzeń
class LogEntry(models.Model):
    ACTION_TYPES = [
        ('USER_CREATED', 'Utworzono użytkownika'),
        ('USER_UPDATED', 'Zaktualizowano użytkownika'),
        ('USER_DELETED', 'Usunięto użytkownika'),
        ('LOGIN_SUCCESS', 'Pomyślne logowanie'),
        ('LOGIN_FAILED', 'Nieudane logowanie'),
        ('PIN_SENT', 'Wysłano PIN 2FA'),
        ('PIN_VERIFIED', 'PIN 2FA zweryfikowany'),
        # Dodaj więcej typów w miarę potrzeb
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Użytkownik wykonujący akcję",
        related_name='custom_log_entries' # Unikalna nazwa, aby uniknąć konfliktu
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Znacznik czasu")
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, verbose_name="Typ akcji")
    details = models.TextField(blank=True, null=True, verbose_name="Szczegóły")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adres IP")

    def __str__(self):
        user_display = str(self.user) if self.user else "System" # Poprawka dla None user
        # Formatowanie daty dla lepszej czytelności
        timestamp_formatted = self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else "Brak daty"
        return f"{timestamp_formatted} - {user_display} - {self.get_action_type_display()}"

    class Meta:
        verbose_name = "Wpis dziennika zdarzeń"
        verbose_name_plural = "Dziennik zdarzeń"
        ordering = ['-timestamp']