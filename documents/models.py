# documents/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
# Importujemy modele z innych aplikacji
try:
    from core.models import Osoba
    from phd_process.models import SzablonZdarzenia, Historia # Potrzebne? Raczej nie.
except ImportError:
    Osoba = None
    # Historia = None

class SzablonDokumentu(models.Model):
    """Szablon dokumentu, np. LaTeX lub inny format"""
    opis = models.TextField(_("Opis szablonu")) # SQL: NOT NULL
    # Przechowujemy plik szablonu
    tresc = models.FileField(_("Plik szablonu (.tex, .docx?)"), upload_to='dokumenty/szablony/', max_length=255, blank=True, null=True) # SQL: PATH -> FileField
    # Można dodać pole na typ szablonu, np. choices=['UCHWALA_RD', 'PISMO_DO_PROMOTORA']

    class Meta:
        verbose_name = _("Szablon dokumentu")
        verbose_name_plural = _("Szablony dokumentów")

    def __str__(self):
        return self.opis[:100] # Skrócony opis


class DokumentWniosekUchwala(models.Model):
    """Reprezentuje wygenerowany dokument, wniosek lub uchwałę"""
    # Zmieniamy nazwę klasy na bardziej standardową
    class TypDokumentuChoices(models.TextChoices):
        WYCHODZACY = 'Wychodzący', _('Wychodzący')
        PRZYCHODZACY = 'Przychodzący', _('Przychodzący')

    data = models.DateField(_("Data dokumentu")) # SQL: NOT NULL
    numer = models.CharField(_("Numer dokumentu"), max_length=255) # SQL: NOT NULL
    # Przechowujemy wygenerowany/zeskanowany dokument PDF
    plik_pdf = models.FileField(_("Plik PDF"), upload_to='dokumenty/wygenerowane/', max_length=255) # SQL: PDFlink PATH -> FileField
    # Zmieniamy nazwę pola Typ... na bardziej opisową
    kierunek = models.CharField(_("Kierunek (Wychodzący/Przychodzący)"), max_length=20, choices=TypDokumentuChoices.choices, null=True, blank=True)
    # Autor i Adresat jako ForeignKey do Osoba
    autor = models.ForeignKey('core.Osoba', verbose_name=_("Autor"), on_delete=models.SET_NULL, null=True, blank=True, related_name='dokumenty_autorskie')
    adresat = models.ForeignKey('core.Osoba', verbose_name=_("Adresat"), on_delete=models.SET_NULL, null=True, blank=True, related_name='dokumenty_adresowane')
    # Powiązanie z użytym szablonem (jeśli dotyczy)
    szablon_uzyty = models.ForeignKey(SzablonDokumentu, verbose_name=_("Użyty szablon"), on_delete=models.SET_NULL, null=True, blank=True, related_name='wygenerowane_dokumenty')
    # Można dodać powiązanie z Historią (jeśli dokument jest wynikiem zdarzenia)
    wpis_historii = models.ForeignKey('phd_process.Historia', verbose_name=_("Powiązane zdarzenie historii"), on_delete=models.SET_NULL, null=True, blank=True, related_name='powiazane_dokumenty')

    class Meta:
        verbose_name = _("Dokument/Wniosek/Uchwała")
        verbose_name_plural = _("Dokumenty/Wnioski/Uchwały")
        ordering = ['-data']

    def __str__(self):
        return f"{self.numer} ({self.data})"