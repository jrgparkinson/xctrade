from django.db import models
from django.contrib.auth.models import User
from .athlete import Athlete
import logging
from decimal import Decimal
from .asset import Share
from .equations import get_equation
from .exceptions import (
    InsufficienFundsException,
    InsufficienSharesException,
    TradingException,
)

LOGGER = logging.getLogger(__name__)


class NotBankException(TradingException):
    status_code = 500
    default_detail = "Entity is not a bank."
    default_code = "not_bank"


class Entity(models.Model):
    INITIAL_CAPITAL = 1000
    capital = models.DecimalField(
        max_digits=10, decimal_places=2, default=INITIAL_CAPITAL
    )
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_bank = models.BooleanField(default=False)

    def vol_owned(self, athlete):
        return Share.vol_for_athlete_entity(athlete, self)

    def can_sell(self, athlete, vol: Decimal):
        if vol == Decimal(0):
            return True

        share = self.get_share(athlete)
        if not share or share.volume < vol:
            return False

        return True

    def can_buy(self, unit_price: Decimal, vol: Decimal):
        return self.capital >= unit_price * vol

    def can_trade(self, athlete, unit_price, vol, buy_or_sell: str):
        if buy_or_sell[0] == "B" and self.can_buy(unit_price, vol):
            return True
        elif buy_or_sell[0] == "S" and self.can_sell(athlete, vol):
            return True
        return False

    def transfer_cash_to(self, seller, price):
        if self.capital < price:
            raise InsufficienFundsException
        self.capital -= price
        seller.capital += price

    def get_share(self, athlete):
        # LOGGER.info(Share.objects.all().filter(athlete=athlete,owner=self))
        share, created = Share.objects.get_or_create(athlete=athlete, owner=self)
        share.save()
        return share

    def add_share(self, athlete, volume):
        share = self.get_share(athlete)
        share.volume += volume
        share.save()

    def subtract_share(self, athlete, volume):
        share = self.get_share(athlete)
        if share.volume < volume:
            raise InsufficienSharesException
        share.volume -= volume
        share.save()

    def transfer_shares_to(self, buyer, athlete, volume):
        if self.vol_owned(athlete) < volume:
            raise InsufficienSharesException

        self.subtract_share(athlete, volume)
        buyer.add_share(athlete, volume)

    @property
    def portfolio_value(self):
        shares = Share.objects.all().filter(owner=self)

        share_value = Decimal(0.0)

        for share in shares:
            if share.athlete.value:
                share_value += round(share.volume * share.athlete.value, 2)

        return self.capital + share_value

    def get_bank_offer(self, athlete, vol, buy_or_sell="Buy"):
        """
        Note: buy or sell is what the bank is doing
        """
        if not self.is_bank:
            raise NotBankException

        current_unit_price = athlete.value

        if not current_unit_price or not vol:
            return None
        bank_price_eq = get_equation(f"bank{buy_or_sell}Price")

        # Prepare as floats
        volume = float(vol)
        current_unit_price = float(current_unit_price)
        offer_total_price = Decimal(round(eval(bank_price_eq), 2))

        unit_price = round(offer_total_price / vol, 2)

        # Check bank can actually do the trade
        if self.can_trade(athlete, unit_price, vol, buy_or_sell):
            # LOGGER.info(f"Bank offer: {athlete.name} ({vol}): {unit_price} per share")
            return unit_price
        else:
            # LOGGER.info(f"Bank offer: {athlete.name} ({vol}): None")
            return None


def get_cowley_club_bank():
    bank_user, created = User.objects.get_or_create(username="cowley_club_bank")
    # bank, created = Entity.objects.get(_or_create(name="Cowley Club Bank", is_bank=True,
    # capital=100000, user=bank_user))
    bank = bank_user.entity
    if created:
        bank.is_bank = True
        bank.capital = 1000000
        bank.name = "Cowley Club Bank"

    bank.save()
    return bank
