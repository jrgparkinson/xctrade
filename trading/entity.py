from django.db import models
from django.contrib.auth.models import User
from .athlete import Athlete
from .asset import Share
from .exceptions import InsufficienFundsException, InsufficienSharesException

class Entity(models.Model):
    INITIAL_CAPITAL = 1000
    capital = models.DecimalField(max_digits=10, decimal_places=2, default=INITIAL_CAPITAL)
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def vol_owned(self, athlete):
        return Share.vol_for_athlete_entity(athlete, self)

    def transfer_cash_to(self, seller, price):
        if self.capital < price:
            raise InsufficienFundsException
        self.capital -= price
        seller.capital += price

    def get_share(self, athlete):
        share, created = Share.objects.get_or_create(athlete=athlete,owner=self)
        return share

    def add_share(self, athlete, volume):
        share = self.get_share(athlete)
        share.volume += volume
        share.save()

    def subtract_share(self, athlete, volume):
        share = self.get_share(athlete)
        share.volume -= volume
        share.save()
    
    def transfer_shares_to(self, buyer, athlete, volume):
        if self.vol_owned(athlete) < volume:
            raise InsufficienSharesException

        self.subtract_share(athlete, volume)
        buyer.add_share(athlete, volume)

