"""Custom user model — login is by email instead of username."""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Manager that uses email as the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        # Username is kept equal to the email so admin lookups still work
        # and legacy Django code that expects a username doesn't break.
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """A user that logs in by email."""

    email = models.EmailField(unique=True)
    # First/last name inherited from AbstractUser.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # email + password are enough to create a user

    objects = UserManager()

    def __str__(self):
        return self.email
