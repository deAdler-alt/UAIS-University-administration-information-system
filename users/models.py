# users/models.py
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# --- Modele zweryfikowane i zaktualizowane zgodnie z Dzień 1 ---

class Wydzial(models.Model):
    nazwa = models.CharField(max_length=255, unique=True, verbose_name="Nazwa wydziału")
    # UWAGA: Dodano pola zgodnie ze schematem SQL (AGPD_*.sql)
    adres_ulica = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ulica")
    adres_miasto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Miasto")
    adres_kod_pocztowy = models.CharField(max_length=20, blank=True, null=True, verbose_name="Kod pocztowy")
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="Email wydziału")
    logo = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ścieżka do logo") # Może lepiej ImageField w przyszłości?
    telefon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon") # Zmieniono z BigInt na CharField dla elastyczności
    www_adres = models.URLField(max_length=255, blank=True, null=True, verbose_name="Adres WWW")

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = "Wydział"
        verbose_name_plural = "Wydziały"
        ordering = ['nazwa']

class RadaDyscypliny(models.Model):
    nazwa = models.CharField(max_length=255, verbose_name="Nazwa rady dyscypliny")
    wydzial = models.ForeignKey(Wydzial, on_delete=models.CASCADE, verbose_name="Wydział", related_name="rady_dyscypliny")
    # UWAGA: Dodano pola zgodnie ze schematem SQL (AGPD_*.sql)
    adres_ulica = models.CharField(max_length=255, verbose_name="Ulica")
    adres_kod_pocztowy = models.CharField(max_length=20, verbose_name="Kod pocztowy") # Zmieniono z 255 na 20
    adres_miasto = models.CharField(max_length=255, verbose_name="Miasto")
    telefon = models.CharField(max_length=50, verbose_name="Telefon") # Zmieniono z BigInt na CharField
    email = models.EmailField(max_length=255, verbose_name="Email rady")
    www_adres = models.URLField(max_length=255, verbose_name="Adres WWW")
    logo = models.CharField(max_length=255, verbose_name="Ścieżka do logo") # Może lepiej ImageField w przyszłości?
    # UWAGA: id_wydzial jest już obsługiwane przez pole 'wydzial' ForeignKey, nie dublujemy go.

    def __str__(self):
        return f"{self.nazwa} ({self.wydzial.nazwa})"

    class Meta:
        verbose_name = "Rada Dyscypliny"
        verbose_name_plural = "Rady Dyscypliny"
        ordering = ['wydzial', 'nazwa']
        # UWAGA: unique_together jest OK, ale w nowszych Django preferuje się constraints w Meta
        constraints = [
            models.UniqueConstraint(fields=['nazwa', 'wydzial'], name='unique_rada_in_wydzial')
        ]
        # unique_together = ('nazwa', 'wydzial') # Można zostawić dla kompatybilności lub usunąć

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator') # Odpowiada 'admin' z .txt
        PRAWNIK = 'PRAWNIK', _('Radca prawny') # Odpowiada 'prawnik' z .txt
        OBSLUGA = 'OBSLUGA', _('Pomoc administracyjna') # Odpowiada 'pomocRD' z .txt
        RADA = 'RADA', _('Zarząd Rady Dyscypliny') # Odpowiada 'zarzadRD' z .txt
        # TODO: Rozważyć dodanie 'ZARZAD_KD' ('Zarząd Komisji Doktorskiej') jeśli potrzebne?

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
        verbose_name="Wydział (jeśli dotyczy)"
    )
    rada_dyscypliny_fk = models.ForeignKey(
        RadaDyscypliny,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Rada Dyscypliny (jeśli dotyczy)"
    )
    # UWAGA: Powiązanie z Uprawnienia - na razie brak bezpośredniej relacji, używamy pola 'role'

    email = models.EmailField(_('adres email'), unique=True) # Zmieniono label
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Usunięto username z REQUIRED_FIELDS, bo USERNAME_FIELD to email

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.email})"
        return self.email

class LogEntry(models.Model):
    # UWAGA: Rozważ dodanie nowych ACTION_TYPES w miarę implementacji kolejnych funkcji
    ACTION_TYPES = [
        ('USER_CREATED', 'Utworzono użytkownika'),
        ('USER_UPDATED', 'Zaktualizowano użytkownika'),
        ('USER_DELETED', 'Usunięto użytkownika'),
        ('LOGIN_SUCCESS', 'Pomyślne logowanie'),
        ('LOGIN_FAILED', 'Nieudane logowanie'),
        ('PIN_SENT', 'Wysłano PIN 2FA'),
        ('PIN_VERIFIED', 'PIN 2FA zweryfikowany'),
        ('DOKTORANT_CREATED', 'Utworzono doktoranta'),
        ('DOKTORANT_UPDATED', 'Zaktualizowano doktoranta'),
        ('DOKTORANT_DELETED', 'Usunięto doktoranta'),
        ('SKLAD_RD_MEMBER_ADDED', 'Dodano członka do składu RD'),
        ('SKLAD_RD_MEMBER_UPDATED', 'Zaktualizowano członkostwo w składzie RD'),
        ('SKLAD_RD_MEMBER_REMOVED', 'Usunięto członka ze składu RD'),
        # (do zrobienia na potem) Dodać typy akcji dla CRUD Osoba, Doktorant, SkladRD, Doktorat, etc.
        # np. ('OSOBA_CREATED', 'Utworzono osobę'), ('DOKTORAT_STATUS_CHANGED', 'Zmieniono status doktoratu')
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
    # UWAGA: Model istnieje, ale jego integracja z User.role wymaga dalszej analizy/decyzji.
    # Na razie jest to tylko słownik nazw uprawnień zgodny z SQL.
    nazwa = models.CharField(max_length=255, unique=True, verbose_name="Nazwa uprawnienia (wg SQL)")

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = "Uprawnienie (wg schematu SQL)"
        verbose_name_plural = "Uprawnienia (wg schematu SQL)"
        ordering = ['nazwa']

class Adres(models.Model):
    # UWAGA: Zgodność pól z SQL - Miasto, KodPocztowy, Ulica, NrBudynku, Afiliacja_*
    miasto = models.CharField(max_length=255, verbose_name="Miasto")
    kod_pocztowy = models.CharField(max_length=20, verbose_name="Kod pocztowy")
    ulica = models.CharField(max_length=255, verbose_name="Ulica")
    nr_budynku = models.CharField(max_length=20, verbose_name="Nr budynku/lokalu") # Dodano /lokalu dla jasności
    afiliacja_uczelnia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Afiliacja - Uczelnia")
    afiliacja_wydzial = models.CharField(max_length=255, blank=True, null=True, verbose_name="Afiliacja - Wydział")
    afiliacja_jednostka = models.CharField(max_length=255, blank=True, null=True, verbose_name="Afiliacja - Jednostka")

    def __str__(self):
        czesci = [f"{self.ulica} {self.nr_budynku}" if self.ulica and self.nr_budynku else self.ulica, # Poprawiono logikę łączenia
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
    # UWAGA: Weryfikacja pól - wszystkie kluczowe pola z .txt i SQL wydają się być obecne.
    PLEC_CHOICES = [ ('M', 'Mężczyzna'), ('K', 'Kobieta'), ]
    imie = models.CharField(max_length=255, verbose_name="Imię")
    nazwisko = models.CharField(max_length=255, verbose_name="Nazwisko")
    tytul_stopien = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tytuł/Stopień naukowy (przed nazwiskiem)")
    email = models.EmailField(max_length=255, unique=True, verbose_name="Adres email")
    stanowisko = models.CharField(max_length=255, blank=True, null=True, verbose_name="Stanowisko")
    telefon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon") # Zgodne z SQL (varchar)
    link_do_profilu_nauka_polska = models.URLField(max_length=255, blank=True, null=True, verbose_name="Link do profilu Nauka Polska/ORCID itp.") # Zmieniono nazwę pola dla jasności
    specjalnosci = models.TextField(blank=True, null=True, verbose_name="Specjalności naukowe")
    plec = models.CharField(max_length=1, choices=PLEC_CHOICES, verbose_name="Płeć")
    tytul_po = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tytuł/Stopień (po nazwisku)")
    # Odmiany imienia i nazwiska - ZGODNE z SQL i .txt
    imie_nazwisko_dopelniacz = models.CharField(max_length=510, verbose_name="Dopełniacz (kogo, czego?)")
    imie_nazwisko_celownik = models.CharField(max_length=510, verbose_name="Celownik (komu, czemu?)")
    imie_nazwisko_biernik = models.CharField(max_length=510, verbose_name="Biernik (kogo, co?)")
    # Relacja do adresów - ZGODNA
    adresy = models.ManyToManyField(Adres, through='Adres_Osoba', verbose_name="Adresy")

    def __str__(self):
        czesci_tytulu = filter(None, [self.tytul_stopien, f"{self.imie} {self.nazwisko}", self.tytul_po])
        return " ".join(czesci_tytulu)

    class Meta:
        verbose_name = "Osoba"
        verbose_name_plural = "Osoby"
        ordering = ['nazwisko', 'imie']

class Adres_Osoba(models.Model):
    # UWAGA: Model pośredniczący - ZGODNY
    osoba = models.ForeignKey(Osoba, on_delete=models.CASCADE, verbose_name="Osoba")
    adres = models.ForeignKey(Adres, on_delete=models.CASCADE, verbose_name="Adres")
    preferowany = models.BooleanField(default=False, verbose_name="Adres preferowany/korespondencyjny")

    def __str__(self):
        return f"{self.osoba} - {self.adres} ({'Preferowany' if self.preferowany else 'Zwykły'})"

    class Meta:
        verbose_name = "Powiązanie Adres-Osoba"
        verbose_name_plural = "Powiązania Adres-Osoba"
        unique_together = ('osoba', 'adres')


class SkladRD(models.Model):
    """Model reprezentujący skład osobowy Rady Dyscypliny."""
    # UWAGA: Model SkladRD - ZGODNY z SQL i logiką
    rd = models.ForeignKey(
        RadaDyscypliny,
        on_delete=models.CASCADE,
        verbose_name="Rada Dyscypliny",
        related_name="sklad"
    )
    osoba = models.ForeignKey(
        Osoba,
        on_delete=models.CASCADE, # Lub PROTECT jeśli osoba nie powinna być usuwana, gdy jest w składzie
        verbose_name="Osoba (Członek Rady)"
    )
    funkcja_czlonka = models.ForeignKey( # Nazwa zgodna z modelem Funkcja_czlonka
        Funkcja_czlonka,
        on_delete=models.PROTECT,
        verbose_name="Funkcja w Radzie"
    )
    data_powolania = models.DateField(null=True, blank=True, verbose_name="Data powołania") # Nazwa zgodna z poprzednią wersją
    aktywny = models.BooleanField(default=True, verbose_name="Członkostwo aktywne")

    def __str__(self):
        return f"{self.osoba} - {self.funkcja_czlonka} w {self.rd.nazwa}"

    class Meta:
        verbose_name = "Skład Rady Dyscypliny"
        verbose_name_plural = "Składy Rad Dyscyplin"
        ordering = ['rd', 'osoba__nazwisko', 'osoba__imie']
        # UWAGA: unique_together zastąpione przez constraints
        constraints = [
            models.UniqueConstraint(fields=['rd', 'osoba'], name='unique_osoba_in_rd')
        ]
        # unique_together = ('rd', 'osoba') # Można usunąć

# --- NOWY MODEL: Doktorant ---
# Zgodnie z decyzją - osobny model
# Pola na podstawie SQL: Doktorant oraz dokumentacji .txt

class Doktorant(models.Model):
    """Model reprezentujący doktoranta."""
    PLEC_CHOICES = [ ('M', 'Mężczyzna'), ('K', 'Kobieta'), ] # Zaciągnięte z modelu Osoba

    # Dane osobowe (zgodnie z SQL Doktorant i .txt Doktorant-RD-XY)
    imie = models.CharField(max_length=255, verbose_name="Imię")
    nazwisko = models.CharField(max_length=255, verbose_name="Nazwisko")
    email = models.EmailField(max_length=255, unique=True, verbose_name="Adres email") # Zakładamy unikalność
    tytul_stopien = models.CharField(max_length=255, verbose_name="Tytuł/Stopień naukowy") # Z SQL 'tytulStopien', z .txt 'tytul-naukowy'
    plec = models.CharField(max_length=1, choices=PLEC_CHOICES, verbose_name="Płeć") # Z .txt

    # Odmiany nazwiska (zgodnie z SQL Doktorant i .txt Doktorant-RD-XY)
    imie_nazwisko_dopelniacz = models.CharField(max_length=510, verbose_name="Dopełniacz (kogo, czego?)")
    imie_nazwisko_celownik = models.CharField(max_length=510, verbose_name="Celownik (komu, czemu?)")
    imie_nazwisko_biernik = models.CharField(max_length=510, verbose_name="Biernik (kogo, co?)")

    # Dane kontaktowe i adresowe (zgodnie z SQL Doktorant)
    # UWAGA: SQL ma osobne pola adresowe, a nie relację do Adres. Implementujemy zgodnie z SQL.
    # Można by rozważyć użycie relacji do Adres jak w Osoba dla spójności, ale trzymamy się schematu.
    adres_ulica = models.CharField(max_length=255, verbose_name="Ulica")
    adres_kod_pocztowy = models.CharField(max_length=20, verbose_name="Kod pocztowy")
    adres_miasto = models.CharField(max_length=255, verbose_name="Miasto")
    telefon = models.CharField(max_length=50, verbose_name="Telefon") # Zgodnie z SQL (varchar)

    # Powiązanie z Radą Dyscypliny (z dokumentacji .txt - pole 'rada')
    # UWAGA: SQL nie ma bezpośredniego powiązania Doktorant -> RD, ale Doktorat -> RD.
    # Logicznie doktorant jest związany z jakąś radą, więc dodajemy to pole zgodnie z .txt.
    # Jeśli doktorant może być związany z wieloma radami (mało prawdopodobne) to ManyToMany.
    # Jeśli tylko z jedną na raz, to ForeignKey. Zakładam ForeignKey.
    rada_dyscypliny = models.ForeignKey(
        RadaDyscypliny,
        on_delete=models.PROTECT, # Chronimy radę przed usunięciem, jeśli ma przypisanych doktorantów? Lub SET_NULL?
        verbose_name="Rada Dyscypliny",
        related_name="doktoranci",
        null=True, # Czy doktorant musi być od razu przypisany do rady?
        blank=True
    )

    def __str__(self):
        tytul = self.tytul_stopien + " " if self.tytul_stopien else ""
        return f"{tytul}{self.imie} {self.nazwisko} ({self.email})"

    class Meta:
        verbose_name = "Doktorant"
        verbose_name_plural = "Doktoranci"
        ordering = ['nazwisko', 'imie']