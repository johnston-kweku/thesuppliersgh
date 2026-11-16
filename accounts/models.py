from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone 
from datetime import timedelta
import random, string, uuid

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



def default_expiry():
    return timezone.now() + timedelta(hours=48)

class Invitation(models.Model):
    token = models.UUIDField(unique=True, default=uuid.uuid4, )
    role = models.CharField(max_length=15, choices=User.Role.choices, )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_by')
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_by')
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=default_expiry)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()
