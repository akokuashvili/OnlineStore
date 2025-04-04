from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from apps.common.models import IsDeletedModel
from .managers import CustomUserManager


ACCOUNT_TYPE_CHOICES = {
    ("SELLER", "SELLER"),
    ("BUYER", "BUYER"),
}


class User(AbstractBaseUser, IsDeletedModel, PermissionsMixin):
    first_name = models.CharField(max_length=50, null=True, verbose_name='First name')
    last_name = models.CharField(max_length=50, null=True, verbose_name='Last name')
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', null=True, default='avatars/default.jpg')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    account_type = models.CharField(max_length=6, choices=ACCOUNT_TYPE_CHOICES, default='BUYER')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name

