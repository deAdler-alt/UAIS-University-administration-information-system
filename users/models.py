# users/models.py
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# --- Istniejące modele ---

class Wydzial(models.Model):
    nazwa = models.CharField(max_length=255, unique=True, verbose_name="Nazwa wydziału")

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = "Wydział"
        verbose_name_plural = "Wydziały"
        ordering = ['nazwa']

class RadaDyscypliny(models.Model):
    nazwa = models.CharField(max_length=255, verbose_name="Nazwa rady dyscypliny")
    wydzial = models.ForeignKey(Wydzial, on_delete=models.CASCADE, verbose_name="Wydział", related_name="rady_dyscypliny")

    def __str__(self):
        return f"{self.nazwa} ({self.wydzial.nazwa})"

    class Meta:
        verbose_name = "Rada Dyscypliny"
        verbose_name_plural = "Rady Dyscypliny"
        ordering = ['wydzial', 'nazwa']
        unique_together = ('nazwa', 'wydzial')

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

    wydzial = models.ForeignKey(
        Wydzial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Wydział"
    )
    rada_dyscypliny_fk = models.ForeignKey(
        RadaDyscypliny,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Rada Dyscypliny"
    )

    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.email})"
        return self.email

class LogEntry(models.Model):
    ACTION_TYPES = [
        ('USER_CREATED', 'Utworzono użytkownika'),
        ('USER_UPDATED', 'Zaktualizowano użytkownika'),
        ('USER_DELETED', 'Usunięto użytkownika'),
        ('LOGIN_SUCCESS', 'Pomyślne logowanie'),
        ('LOGIN_FAILED', 'Nieudane logowanie'),
        ('PIN_SENT', 'Wysłano PIN 2FA'),
        ('PIN_VERIFIED', 'PIN 2FA zweryfikowany'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Użytkownik wykonujący akcję",
        related_name='custom_log_entries'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Znacznik czasu")
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, verbose_name="Typ akcji")
    details = models.TextField(blank=True, null=True, verbose_name="Szczegóły")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adres IP")

    def __str__(self):
        user_display = str(self.user) if self.user else "System"
        timestamp_formatted = self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else "Brak daty"
        return f"{timestamp_formatted} - {user_display} - {self.get_action_type_display()}"

    class Meta:
        verbose_name = "Wpis dziennika zdarzeń"
        verbose_name_plural = "Dziennik zdarzeń"
        ordering = ['-timestamp']

class Funkcja_czlonka(models.Model):
    nazwa = models.CharField(max_length=255, unique=True, verbose_name="Nazwa funkcji")

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = "Funkcja członka (Rady/Komisji)"
        verbose_name_plural = "Funkcje członków (Rady/Komisji)"
        ordering = ['nazwa']

class Uprawnienia(models.Model):
    nazwa = models.CharField(max_length=255, unique=True, verbose_name="Nazwa uprawnienia")

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = "Uprawnienie (wg schematu SQL)"
        verbose_name_plural = "Uprawnienia (wg schematu SQL)"
        ordering = ['nazwa']

class Adres(models.Model):
    miasto = models.CharField(max_length=255, verbose_name="Miasto")
    kod_pocztowy = models.CharField(max_length=20, verbose_name="Kod pocztowy")
    ulica = models.CharField(max_length=255, verbose_name="Ulica")
    nr_budynku = models.CharField(max_length=20, verbose_name="Nr budynku/lokalu")
    afiliacja_uczelnia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Afiliacja - Uczelnia")
    afiliacja_wydzial = models.CharField(max_length=255, blank=True, null=True, verbose_name="Afiliacja - Wydział")
    afiliacja_jednostka = models.CharField(max_length=255, blank=True, null=True, verbose_name="Afiliacja - Jednostka")

    def __str__(self):
        czesci = [f"{self.ulica} {self.nr_budynku}" if self.ulica else None,
                 f"{self.kod_pocztowy} {self.miasto}" if self.kod_pocztowy and self.miasto else self.miasto]
        adres_str = ", ".join(filter(None, czesci))
        afiliacja_czesci = filter(None, [self.afiliacja_jednostka, self.afiliacja_wydzial, self.afiliacja_uczelnia])
        afiliacja_str = ", ".join(afiliacja_czesci)
        if adres_str and afiliacja_str: return f"{adres_str} ({afiliacja_str})"
        elif adres_str: return adres_str
        elif afiliacja_str: return f"Afiliacja: {afiliacja_str}"
        else: return f"Adres ID: {self.pk}"

    class Meta:
        verbose_name = "Adres"
        verbose_name_plural = "Adresy"

class Osoba(models.Model):
    PLEC_CHOICES = [ ('M', 'Mężczyzna'), ('K', 'Kobieta'), ]
    imie = models.CharField(max_length=255, verbose_name="Imię")
    nazwisko = models.CharField(max_length=255, verbose_name="Nazwisko")
    tytul_stopien = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tytuł/Stopień naukowy (przed nazwiskiem)")
    email = models.EmailField(max_length=255, unique=True, verbose_name="Adres email")
    stanowisko = models.CharField(max_length=255, blank=True, null=True, verbose_name="Stanowisko")
    telefon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon")
    link_do_profilu_nauka_polska = models.URLField(max_length=255, blank=True, null=True, verbose_name="Link do profilu Nauka Polska/ORCID itp.")
    specjalnosci = models.TextField(blank=True, null=True, verbose_name="Specjalności naukowe")
    plec = models.CharField(max_length=1, choices=PLEC_CHOICES, verbose_name="Płeć")
    tytul_po = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tytuł/Stopień (po nazwisku)")
    imie_nazwisko_dopelniacz = models.CharField(max_length=510, verbose_name="Dopełniacz (kogo, czego?)")
    imie_nazwisko_celownik = models.CharField(max_length=510, verbose_name="Celownik (komu, czemu?)")
    imie_nazwisko_biernik = models.CharField(max_length=510, verbose_name="Biernik (kogo, co?)")
    adresy = models.ManyToManyField(Adres, through='Adres_Osoba', verbose_name="Adresy")

    def __str__(self):
        czesci_tytulu = filter(None, [self.tytul_stopien, f"{self.imie} {self.nazwisko}", self.tytul_po])
        return " ".join(czesci_tytulu)

    class Meta:
        verbose_name = "Osoba"
        verbose_name_plural = "Osoby"
        ordering = ['nazwisko', 'imie']

class Adres_Osoba(models.Model):
    osoba = models.ForeignKey(Osoba, on_delete=models.CASCADE, verbose_name="Osoba")
    adres = models.ForeignKey(Adres, on_delete=models.CASCADE, verbose_name="Adres")
    preferowany = models.BooleanField(default=False, verbose_name="Adres preferowany/korespondencyjny")

    def __str__(self):
        return f"{self.osoba} - {self.adres} ({'Preferowany' if self.preferowany else 'Zwykły'})"

    class Meta:
        verbose_name = "Powiązanie Adres-Osoba"
        verbose_name_plural = "Powiązania Adres-Osoba"
        unique_together = ('osoba', 'adres')


# --- NOWY Model SkladRD ---

class SkladRD(models.Model):
    """Model reprezentujący skład osobowy Rady Dyscypliny."""
    # Zgodnie ze schematem SQL: id, RD, osoba, funkcja_czlonka_RD, dataPowolania, aktywny

    rd = models.ForeignKey(
        RadaDyscypliny,
        on_delete=models.CASCADE, # Usunięcie rady usuwa powiązane wpisy w składzie
        verbose_name="Rada Dyscypliny",
        related_name="sklad" # Umożliwia dostęp do składu z poziomu obiektu Rady Dyscypliny
    )
    osoba = models.ForeignKey(
        Osoba,
        on_delete=models.CASCADE, # Usunięcie osoby usuwa jej wpisy w składach
        # Można rozważyć PROTECT, jeśli nie chcemy usuwać osoby, która jest w jakimś składzie
        verbose_name="Osoba (Członek Rady)"
    )
    funkcja_czlonka = models.ForeignKey(
        Funkcja_czlonka,
        on_delete=models.PROTECT, # Chroni przed usunięciem funkcji, jeśli jest używana
        verbose_name="Funkcja w Radzie"
        # Zmieniono nazwę pola z 'funkcja_czlonka_RD' na 'funkcja_czlonka' dla spójności
    )
    data_powolania = models.DateField(null=True, blank=True, verbose_name="Data powołania")
    # Zmieniono nazwę pola z 'dataPowolania' na 'data_powolania'
    aktywny = models.BooleanField(default=True, verbose_name="Członkostwo aktywne")

    def __str__(self):
        return f"{self.osoba} - {self.funkcja_czlonka} w {self.rd.nazwa}"

    class Meta:
        verbose_name = "Skład Rady Dyscypliny"
        verbose_name_plural = "Składy Rad Dyscyplin"
        ordering = ['rd', 'osoba__nazwisko', 'osoba__imie'] # Sortowanie wg rady, potem nazwiska członka
        unique_together = ('rd', 'osoba') # Zapobiega dodaniu tej samej osoby wielokrotnie do tej samej rady