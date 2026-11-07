from django.db import models
from django.contrib.auth.models import AbstractUser
import random, string
# Create your models here.



class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        VENDOR = 'VENDOR', 'Vendor'
        CUSTOMER = 'CUSTOMER', 'Customer'


    full_name = models.CharField(max_length=100, null=True)
    role = models.CharField(max_length=15, choices=Role.choices)
    public_id = models.CharField(max_length=12, unique=True, editable=False, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)

    def is_admin(self): return self.role == self.Role.ADMIN

    def is_customer(self): return self.role == self.Role.CUSTOMER

    def is_vendor(self): return self.role == self.Role.VENDOR

    ROLE_PREFIX = {
        Role.VENDOR: 'VEN',
        Role.CUSTOMER: 'CUS',
        Role.ADMIN: 'ADM'
    }

    def save(self, *args, **kwargs):
        if not self.public_id:
            prefix = self.ROLE_PREFIX.get(self.role, 'USR')
            while True:
                suffix = "".join(random.choices(string.digits, k=6))
                candidate = f'{prefix}-{suffix}'
                if not User.objects.filter(public_id=candidate).exists():
                    self.public_id = candidate
                    break

        if not self.username:
            self.username = self.public_id

        return super().save(*args, **kwargs)