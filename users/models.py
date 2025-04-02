from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrator'),
        ('PRAWNIK', 'Prawnik'),
        ('OBSLUGA', 'Obsługa'),
        ('RADA', 'Rada'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='RADA')
