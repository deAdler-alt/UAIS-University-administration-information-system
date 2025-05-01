# core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

# Zakładamy, że te modele już tu są z poprzedniego kroku:
class Wydzial(models.Model):
    nazwa = models.CharField(_("Nazwa wydziału"), max_length=255, unique=True)
    adres_ulica = models.CharField(_("Ulica"), max_length=255)
    adres_miasto = models.CharField(_("Miasto"), max_length=255)
    adres_kod_pocztowy = models.CharField(_("Kod pocztowy"), max_length=10)
    email = models.EmailField(_("Email wydziału"), max_length=255, blank=True)
    telefon = models.CharField(_("Telefon"), max_length=50, blank=True)
    logo = models.CharField(_("Ścieżka/URL do logo"), max_length=255, blank=True)
    www_adres = models.URLField(_("Adres WWW"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Wydział")
        verbose_name_plural = _("Wydziały")
        ordering = ['nazwa']

    def __str__(self):
        return self.nazwa

class FunkcjaCzlonka(models.Model):
    nazwa = models.CharField(_("Nazwa funkcji"), max_length=255, unique=True)

    class Meta:
        verbose_name = _("Funkcja członka")
        verbose_name_plural = _("Funkcje członków")
        ordering = ['nazwa']

    def __str__(self):
        return self.nazwa

class Adres(models.Model):
    miasto = models.CharField(_("Miasto"), max_length=255)
    kod_pocztowy = models.CharField(_("Kod pocztowy"), max_length=10)
    ulica = models.CharField(_("Ulica"), max_length=255)
    nr_budynku = models.CharField(_("Nr budynku/lokalu"), max_length=50)
    afiliacja_uczelnia = models.CharField(_("Afiliacja - Uczelnia"), max_length=255, blank=True, null=True) # Ustawiamy null=True dla opcjonalnych CharField
    afiliacja_wydzial = models.CharField(_("Afiliacja - Wydział"), max_length=255, blank=True, null=True)
    afiliacja_jednostka = models.CharField(_("Afiliacja - Jednostka"), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _("Adres")
        verbose_name_plural = _("Adresy")

    def __str__(self):
        parts = [self.ulica, self.nr_budynku, self.kod_pocztowy, self.miasto]
        return ", ".join(filter(None, parts))

class RD(models.Model):
    """Reprezentuje Radę Dyscypliny"""
    nazwa = models.CharField(_("Nazwa rady"), max_length=255, unique=True)
    adres_ulica = models.CharField(_("Ulica"), max_length=255)
    adres_kod_pocztowy = models.CharField(_("Kod pocztowy"), max_length=10)
    adres_miasto = models.CharField(_("Miasto"), max_length=255)
    telefon = models.CharField(_("Telefon"), max_length=50) # Zakładamy NOT NULL z SQL
    email = models.EmailField(_("Email rady"), max_length=255)
    www_adres = models.URLField(_("Adres WWW"), max_length=255)
    logo = models.CharField(_("Ścieżka/URL do logo"), max_length=255) # Zakładamy NOT NULL z SQL
    # Relacja do Wydzialu - chronimy przed usunięciem wydziału, jeśli są powiązane rady
    wydzial = models.ForeignKey(Wydzial, verbose_name=_("Wydział"), on_delete=models.PROTECT, related_name='rady_dyscyplin')

    class Meta:
        verbose_name = _("Rada Dyscypliny")
        verbose_name_plural = _("Rady Dyscyplin")
        ordering = ['nazwa']

    def __str__(self):
        return self.nazwa

class Osoba(models.Model):
    """Szczegółowe dane osoby (pracownika, recenzenta, itp.)"""
    # Opcje dla płci
    class PlecChoices(models.TextChoices):
        MEZCZYZNA = 'M', _('Mężczyzna')
        KOBIETA = 'K', _('Kobieta')
        INNA = 'I', _('Inna') # Opcjonalnie

    imie = models.CharField(_("Imię"), max_length=255)
    nazwisko = models.CharField(_("Nazwisko"), max_length=255)
    tytul_stopien = models.CharField(_("Tytuł/Stopień naukowy"), max_length=255, blank=True, null=True) # Może być pusty
    email = models.EmailField(_("Email"), max_length=255, unique=True) # Zakładamy, że email osoby jest unikalny
    stanowisko = models.CharField(_("Stanowisko"), max_length=255) # Zakładamy NOT NULL
    telefon = models.CharField(_("Telefon"), max_length=50, blank=True, null=True)
    link_do_profilu_gov = models.URLField(_("Link do Profilu Nauka Polska/Gov"), max_length=255, blank=True, null=True)
    specjalnosci = models.CharField(_("Specjalności"), max_length=255, blank=True, null=True)
    plec = models.CharField(_("Płeć"), max_length=1, choices=PlecChoices.choices) # Używamy choices
    tytul_po = models.CharField(_("Tytuł po nazwisku (np. prof. ucz.)"), max_length=255, blank=True, null=True)
    # Odmiany imienia i nazwiska
    imie_nazwisko_dopelniacz = models.CharField(_("Imię Nazwisko (Dopełniacz)"), max_length=255)
    imie_nazwisko_celownik = models.CharField(_("Imię Nazwisko (Celownik)"), max_length=255)
    imie_nazwisko_biernik = models.CharField(_("Imię Nazwisko (Biernik)"), max_length=255)
    # Relacja do adresów (wiele do wielu przez model pośredni)
    adresy = models.ManyToManyField(Adres, through='AdresOsoba', verbose_name=_("Adresy"), blank=True)

    class Meta:
        verbose_name = _("Osoba")
        verbose_name_plural = _("Osoby")
        ordering = ['nazwisko', 'imie']
        unique_together = [['imie', 'nazwisko', 'email']] # Zapewnia unikalność kombinacji

    def __str__(self):
        return f"{self.tytul_stopien or ''} {self.imie} {self.nazwisko}".strip()

    def get_full_name(self):
         return f"{self.imie} {self.nazwisko}".strip()

class AdresOsoba(models.Model):
    """Model pośredniczący dla relacji Osoba-Adres, przechowuje informację o preferowanym adresie"""
    osoba = models.ForeignKey(Osoba, on_delete=models.CASCADE)
    adres = models.ForeignKey(Adres, on_delete=models.CASCADE)
    preferowany = models.BooleanField(_("Adres preferowany?"), default=False)

    class Meta:
        verbose_name = _("Przypisanie adresu do osoby")
        verbose_name_plural = _("Przypisania adresów do osób")
        unique_together = [['osoba', 'adres']] # Jedno przypisanie danego adresu do danej osoby

    def __str__(self):
        pref = "[P]" if self.preferowany else ""
        return f"{self.osoba} - {self.adres} {pref}"