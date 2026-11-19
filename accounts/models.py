import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import IntegrityError, models, transaction
from django.utils import timezone


class UserManager(DjangoUserManager):
    """Username is optional; User.save() assigns one from the public_id."""

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('An email address is required')
        user = self.model(
            username=username or '',
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        VENDOR = 'VENDOR', 'Vendor'
        CUSTOMER = 'CUSTOMER', 'Customer'

    ROLE_PREFIX = {
        Role.VENDOR: 'VEN',
        Role.CUSTOMER: 'CUS',
        Role.ADMIN: 'ADM',
    }
    PUBLIC_ID_MAX_ATTEMPTS = 5

    full_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.ADMIN)
    public_id = models.CharField(max_length=12, unique=True, editable=False, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)

    objects = UserManager()
    REQUIRED_FIELDS = ['email', 'phone_number']

    def is_admin(self): return self.role == self.Role.ADMIN
    def is_customer(self): return self.role == self.Role.CUSTOMER
    def is_vendor(self): return self.role == self.Role.VENDOR

    def _generate_public_id(self):
        prefix = self.ROLE_PREFIX.get(self.role, 'USR')
        return f'{prefix}-{secrets.randbelow(10**6):06d}'

    def save(self, *args, **kwargs):
        if self.public_id:
            return super().save(*args, **kwargs)

        auto_username = not self.username

        for _ in range(self.PUBLIC_ID_MAX_ATTEMPTS):
            candidate = self._generate_public_id()
            self.public_id = candidate
            if auto_username:
                self.username = candidate
            try:
                # Savepoint: a failed insert must not break an outer transaction.
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                # Reset so the instance is never left half-assigned.
                self.public_id = ''
                if auto_username:
                    self.username = ''
                # Retry only if OUR generated value collided. Anything else
                # (duplicate email, phone) is a real error and must surface.
                collided = User.objects.filter(
                    models.Q(public_id=candidate) | models.Q(username=candidate)
                ).exists()
                if not collided:
                    raise

        raise RuntimeError(
            f'Could not generate a unique public_id after {self.PUBLIC_ID_MAX_ATTEMPTS} attempts'
        )




def default_expiry():
    return timezone.now() < timedelta(hours=48)

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