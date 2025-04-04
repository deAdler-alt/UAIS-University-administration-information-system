from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrator'),
        ('PRAWNIK', 'Prawnik'),
        ('OBSLUGA', 'Obsługa'),
        ('RADA', 'Rada'),
    )
    role = models.CharField(max_length=10, choices=ROLES, null=False, blank=False)

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role == 'RADA':
            self.role = 'ADMIN'
        super().save(*args, **kwargs)