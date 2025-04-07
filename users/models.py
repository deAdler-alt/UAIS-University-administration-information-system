from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _ 

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        PRAWNIK = 'PRAWNIK', _('Radca prawny')
        OBSLUGA = 'OBSLUGA', _('Obsługa administracyjna')
        RADA = 'RADA', _('Członek rady wydziału')

    role = models.CharField(
        _('Rola'),
        max_length=50,
        choices=Role.choices,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username