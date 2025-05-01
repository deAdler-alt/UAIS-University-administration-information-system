# phd_process/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
# Importujemy modele z innych aplikacji, których będziemy potrzebować
from core.models import Osoba, RD, FunkcjaCzlonka

# TODO: Potrzebujemy modelu Doktorant. Czy to po prostu Osoba?
# SQL definiuje osobną tabelę Doktorant z częściowo pokrywającymi się polami.
# Podejście 1: Doktorant to OSOBA + dodatkowe info (np. status, data rozpoczęcia)
# Podejście 2: Osobny model Doktorant (jak w SQL), ale z relacją do Osoba?
# Podejście 3 (Uproszczone na razie): Zakładamy, że doktorant jest po prostu OSOBĄ.
# W modelu Doktorat, pole 'doktorant' będzie ForeignKey do 'core.Osoba'.
# Jeśli potrzebne będą specyficzne dane doktoranta, dodamy model Doktorant później.

class SzablonZdarzenia(models.Model):
    """Np. 'Złożenie wniosku', 'Powołanie komisji', 'Wyznaczenie recenzentów'"""
    opis = models.TextField(_("Opis szablonu zdarzenia"))

    class Meta:
        verbose_name = _("Szablon zdarzenia")
        verbose_name_plural = _("Szablony zdarzeń")
        ordering = ['opis']

    def __str__(self):
        return self.opis


class Doktorat(models.Model):
    """Główny model reprezentujący przewód doktorski"""
    class TrybStudiowChoices(models.TextChoices):
        SZKOLA = 'SZKOLA', _('Szkoła Doktorska')
        EKSTERN = 'EKSTERN', _('Tryb eksternistyczny')

    # Klucze obce - używamy PROTECT lub SET_NULL, aby uniknąć utraty danych
    rada_dyscypliny = models.ForeignKey('core.RD', verbose_name=_("Rada Dyscypliny"), on_delete=models.PROTECT, related_name='doktoraty')
    # Zakładamy (na razie), że doktorant to Osoba
    doktorant = models.ForeignKey('core.Osoba', verbose_name=_("Doktorant"), on_delete=models.PROTECT, related_name='przewody_doktorskie')
    promotor = models.ForeignKey('core.Osoba', verbose_name=_("Promotor"), on_delete=models.PROTECT, related_name='promotor_w_doktoratach')
    promotor_pomocniczy = models.ForeignKey('core.Osoba', verbose_name=_("Promotor pomocniczy"), on_delete=models.SET_NULL, null=True, blank=True, related_name='promotor_pom_w_doktoratach')
    kopromotor = models.ForeignKey('core.Osoba', verbose_name=_("Kopromotor"), on_delete=models.SET_NULL, null=True, blank=True, related_name='kopromotor_w_doktoratach')

    tytul = models.CharField(_("Tytuł rozprawy"), max_length=500, blank=True, null=True) # SQL miał 255, ale tytuły bywają dłuższe
    tryb = models.CharField(_("Tryb studiów"), max_length=10, choices=TrybStudiowChoices.choices, blank=True, null=True) # Dodane pole na podstawie planu
    # Przechowujemy ścieżkę lub plik rozprawy
    rozprawa = models.FileField(_("Plik rozprawy"), upload_to='doktoraty/rozprawy/', max_length=255, blank=True, null=True) # SQL: PATH -> FileField
    komentarz = models.TextField(_("Komentarz/Uwagi"), blank=True, null=True) # SQL: VARCHAR(255) -> TextField

    # Pola związane z datami i uchwałami (z planu/flowchartu) - mogą być opcjonalne
    data_zlozenia_wniosku = models.DateField(_("Data złożenia wniosku o wszczęcie"), null=True, blank=True)
    uchwala_promotor_wszczecie_data = models.DateField(_("Data uchwały (promotor/wszczęcie)"), null=True, blank=True)
    uchwala_promotor_wszczecie_nr = models.CharField(_("Nr uchwały (promotor/wszczęcie)"), max_length=100, blank=True, null=True)
    # ... (można dodać więcej pól dat/numerów uchwał zgodnie z flowchartem) ...
    data_obrony = models.DateField(_("Data obrony"), null=True, blank=True)
    uchwala_nadanie_stopnia_rd_data = models.DateField(_("Data uchwały RD (nadanie stopnia)"), null=True, blank=True)
    uchwala_nadanie_stopnia_rd_nr = models.CharField(_("Nr uchwały RD (nadanie stopnia)"), max_length=100, blank=True, null=True)
    wyroznienie = models.BooleanField(_("Wyróżnienie?"), null=True, blank=True) # Znak zapytania z SQL jest niepoprawny

    # Komisja doktorska jest powiązana przez model KomisjaDr (relacja wiele do wielu z osobami)
    # Pole komisjaDr VECTOR ARRAY z SQL pomijamy - realizujemy przez model KomisjaDr

    class Meta:
        verbose_name = _("Przewód doktorski")
        verbose_name_plural = _("Przewody doktorskie")
        ordering = ['-id'] # Najnowsze najpierw

    def __str__(self):
        return f"Doktorat {self.doktorant}: {self.tytul or 'Brak tytułu'}"

class KomisjaDr(models.Model):
    """Członek komisji doktorskiej dla danego doktoratu"""
    doktorat = models.ForeignKey(Doktorat, verbose_name=_("Doktorat"), on_delete=models.CASCADE, related_name='czlonkowie_komisji') # Usunięcie doktoratu usuwa powiązania komisji
    czlonek = models.ForeignKey('core.Osoba', verbose_name=_("Członek komisji"), on_delete=models.PROTECT, related_name='w_komisjach') # Chronimy Osobę
    # SET_NULL - jeśli funkcja zostanie usunięta, ustawiamy NULL
    funkcja_czlonka = models.ForeignKey('core.FunkcjaCzlonka', verbose_name=_("Funkcja w komisji"), on_delete=models.SET_NULL, null=True, blank=True)
    # SQL miał dataPowolania BIGINT - zakładamy, że to data. Jeśli timestamp, użyj DateTimeField.
    data_powolania = models.DateField(_("Data powołania"), null=True, blank=True) # SQL miał NOT NULL, ale data może nie być znana od razu?
    aktywny = models.BooleanField(_("Aktywny członek?"), default=True) # SQL miał NOT NULL

    class Meta:
        verbose_name = _("Członek komisji doktorskiej")
        verbose_name_plural = _("Członkowie komisji doktorskich")
        unique_together = [['doktorat', 'czlonek']] # Dana osoba może być tylko raz w danej komisji

    def __str__(self):
        return f"{self.czlonek} - {self.funkcja_czlonka or ''} w komisji dr {self.doktorat.id}"

class Recenzent(models.Model):
    """Recenzent przypisany do doktoratu"""
    doktorat = models.ForeignKey(Doktorat, verbose_name=_("Doktorat"), on_delete=models.CASCADE, related_name='recenzenci')
    osoba = models.ForeignKey('core.Osoba', verbose_name=_("Recenzent"), on_delete=models.PROTECT, related_name='recenzje')
    aktywny = models.BooleanField(_("Aktywny recenzent?"), default=True) # SQL: NOT NULL
    # Plik z recenzją - opcjonalny
    recenzja = models.FileField(_("Plik recenzji"), upload_to='doktoraty/recenzje/', max_length=255, blank=True, null=True) # SQL: VARCHAR -> FileField
    data_przyjecia_rozprawy = models.DateField(_("Data przyjęcia rozprawy przez recenzenta"), null=True, blank=True)
    data_wykonania_recenzji = models.DateField(_("Data wykonania recenzji"), null=True, blank=True)
    # Wyróżnienie przez recenzenta
    wyroznienie = models.BooleanField(_("Wyróżnienie recenzenta?"), null=True, blank=True) # SQL: wyroznienie?

    class Meta:
        verbose_name = _("Recenzent")
        verbose_name_plural = _("Recenzenci")
        unique_together = [['doktorat', 'osoba']] # Dana osoba może być tylko raz recenzentem danego doktoratu

    def __str__(self):
        return f"Recenzent {self.osoba} dla dr {self.doktorat.id}"

class SkladRD(models.Model):
    """Członek składu Rady Dyscypliny"""
    rd = models.ForeignKey('core.RD', verbose_name=_("Rada Dyscypliny"), on_delete=models.CASCADE, related_name='sklad')
    osoba = models.ForeignKey('core.Osoba', verbose_name=_("Osoba"), on_delete=models.CASCADE, related_name='w_radach')
    # SET_NULL, bo funkcja może zostać usunięta
    funkcja_czlonka_rd = models.ForeignKey('core.FunkcjaCzlonka', verbose_name=_("Funkcja w Radzie"), on_delete=models.SET_NULL, null=True, blank=True) # SQL miał NOT NULL?
    data_powolania = models.DateField(_("Data powołania"), null=True, blank=True)
    aktywny = models.BooleanField(_("Aktywny w składzie?"), default=True)

    class Meta:
        verbose_name = _("Członek składu Rady Dyscypliny")
        verbose_name_plural = _("Składy Rad Dyscyplin")
        unique_together = [['rd', 'osoba']] # Dana osoba tylko raz w danej radzie

    def __str__(self):
         return f"{self.osoba} - {self.funkcja_czlonka_rd or ''} w {self.rd}"

class Historia(models.Model):
    """Wpis w historii przewodu doktorskiego"""
    doktorat = models.ForeignKey(Doktorat, verbose_name=_("Doktorat"), on_delete=models.CASCADE, related_name='historia')
    data = models.DateField(_("Data zdarzenia")) # SQL: NOT NULL
    opis = models.TextField(_("Opis zdarzenia"), blank=True, null=True) # SQL: TEXT
    # SET_NULL - jeśli szablon zostanie usunięty, historia nadal istnieje
    szablon_zdarzenia = models.ForeignKey(SzablonZdarzenia, verbose_name=_("Szablon zdarzenia"), on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Wpis historii doktoratu")
        verbose_name_plural = _("Historia doktoratów")
        ordering = ['-data', '-id'] # Najnowsze wpisy pierwsze

    def __str__(self):
        return f"{self.data} - {self.szablon_zdarzenia or self.opis[:50]}"

# Model Doktorant - jeśli potrzebujemy więcej specyficznych pól niż w Osoba
# Na razie zakładamy, że doktorant to Osoba (ForeignKey w Doktorat)
# class Doktorant(models.Model):
#     osoba = models.OneToOneField('core.Osoba', on_delete=models.CASCADE)
#     # ... specyficzne pola doktoranta ...