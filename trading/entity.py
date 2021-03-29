from django.db import models

class Entity(models.Model):
    INITIAL_CAPITAL = 1000

    name = models.CharField(max_length=100, unique=True)
    capital = models.DecimalField(max_digits=10, decimal_places=2, default=INITIAL_CAPITAL)
