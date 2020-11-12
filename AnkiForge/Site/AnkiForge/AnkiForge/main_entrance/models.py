from django.db import models
from django.contrib.auth.models import AbstractUser


class Simple(models.Model):
    atest = models.CharField( max_length=50)


class User(AbstractUser):
    pass
# Create your models here.
