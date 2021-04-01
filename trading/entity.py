from django.db import models
from django.contrib.auth.models import User

class Entity(models.Model):
    INITIAL_CAPITAL = 1000
    capital = models.DecimalField(max_digits=10, decimal_places=2, default=INITIAL_CAPITAL)
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

