from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        # Zachowujemy poprzednie WARTOŚCI wewnętrzne, aktualizujemy ew. nazwy wyświetlane
        ADMIN = 'ADMIN', _('Administrator')
        PRAWNIK = 'PRAWNIK', _('Radca prawny')
        OBSLUGA = 'OBSLUGA', _('Pomoc administracyjna') # Zmieniona nazwa wyświetlana
        RADA = 'RADA', _('Zarząd Rady Dyscypliny')     # Zmieniona nazwa wyświetlana

    role = models.CharField(
        _('Rola'),
        max_length=50,
        choices=Role.choices,
        null=True,
        blank=True
    )

    rada_wydzialu = models.CharField(
        _('Rada/Jednostka'),
        max_length=255,
        blank=True, # Pole może być puste
        default='Wydział Elektrotechniki i Informatyki' # Domyślna wartość
    )

 # Zalecane, jeśli email ma być głównym identyfikatorem
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
