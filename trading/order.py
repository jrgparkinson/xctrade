from django.db import models
from datetime import datetime
from decimal import Decimal
import pytz
from .asset import Asset, Share
from .entity import Entity
from .athlete import Athlete
from .exceptions import InvalidOrderException
import logging

LOGGER = logging.getLogger(__name__)


class Trade(models.Model):
    """ History of a trade """

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    buyer = models.ForeignKey(
        Entity, related_name="%(app_label)s_%(class)s_buyer", on_delete=models.CASCADE
    )
    seller = models.ForeignKey(
        Entity, related_name="%(app_label)s_%(class)s_seller", on_delete=models.CASCADE
    )
    unit_price = models.DecimalField(decimal_places=2, max_digits=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.unit_price = Decimal(round(self.unit_price, 2))
        self.volume = Decimal(round(self.volume, 2))
        super(Trade, self).save(*args, **kwargs)

    def do_trade(self):
        price = self.unit_price * self.volume
        self.buyer.transfer_cash_to(self.seller, price)
        self.seller.transfer_shares_to(self.buyer, self.athlete, self.volume)

        LOGGER.info(
            f"Do trade: {self.athlete.name} ({self.volume}) from {self.seller.name} to {self.buyer.name} for {price}"
        )

        self.buyer.save()
        self.seller.save()

    def __str__(self):
        return f"Trade: {self.athlete.name} ({self.volume}) from {self.seller.name} to {self.buyer.name} at {self.unit_price}/share"

    def __repr__(self):
        return self.__str__()


class Order(models.Model):
    """
    Order to buy or sell something
    """

    BUY = "B"
    SELL = "S"
    TYPES = ((BUY, "Buy"), (SELL, "Sell"))

    OPEN = "O"
    FULFILLED = "F"
    PARTIALLY_FILLED = "P"
    CANCELLED = "C"  # maybe just delete the order instead?
    STATUSES = (
        (OPEN, "Open"),
        (FULFILLED, "Fulfilled"),
        (PARTIALLY_FILLED, "Partially filled"),
        (CANCELLED, "Cancelled"),
    )

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    unfilled_volume = models.DecimalField(max_digits=10, decimal_places=2)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    unit_price = models.DecimalField(decimal_places=2, max_digits=10)
    buy_sell = models.CharField(max_length=1, choices=TYPES, default=BUY)
    status = models.CharField(max_length=1, choices=STATUSES, default=OPEN)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    # traded_at = models.DateTimeField(null=True)

    def __repr__(self):
        return f"{self.buy_sell}: {self.athlete} ({self.unfilled_volume}/{self.volume}) @ {self.unit_price} - {self.status}"

    def __str__(self):
        return self.__repr__()

    def save(self, *args, **kwargs):
        self.unit_price = Decimal(round(self.unit_price, 2))
        self.volume = Decimal(round(self.volume, 2))
        if not self.pk:
            self.unfilled_volume = self.volume

            # Check creator can fulfil order
            if not self.can_fulfil(self.unfilled_volume):
                raise InvalidOrderException

        if self.unfilled_volume == 0.0 and self.status == Order.OPEN:
            self.status = Order.FULFILLED

        super(Order, self).save(*args, **kwargs)

    def opposite_buy_sell(self):
        return Order.BUY if self.buy_sell == Order.SELL else Order.SELL

    @property
    def buy_sell_long(self):
        return "Buy" if self.is_buy() else "Sell"

    @property
    def opposite_buy_sell_long(self):
        return "Buy" if self.opposite_buy_sell() == Order.BUY else "Sell"

    def is_buy(self):
        return self.buy_sell == Order.BUY

    def is_sell(self):
        return self.buy_sell == Order.SELL

    def can_fulfil(self, volume):
        volume = Decimal(volume)
        if self.is_buy():
            return self.entity.capital >= self.unit_price * volume
        else:
            return Share.vol_for_athlete_entity(self.athlete, self.entity) >= volume

    def fill_with(self, other, volume):
        """ Fill order with another """
        if not (self.can_fulfil(volume) and other.can_fulfil(volume)):
            raise InvalidOrderException

        if self.entity == other.entity:
            raise InvalidOrderException

        if self.buy_sell == other.buy_sell:
            raise InvalidOrderException

        if self.athlete != other.athlete:
            raise InvalidOrderException

        buy_price = self.unit_price if self.is_buy() else other.unit_price
        sell_price = self.unit_price if self.is_sell() else other.unit_price

        if buy_price < sell_price:
            raise InvalidOrderException

        matched_price = round((buy_price + sell_price) / Decimal(2.0), 2)

        self.unfilled_volume -= volume
        other.unfilled_volume -= volume

        buyer = self.entity if self.is_buy() else other.entity
        seller = self.entity if self.is_sell() else other.entity

        # Now handled by the trade save object
        # price = volume * matched_price
        # buyer.transfer_cash_to(seller, price)
        # seller.transfer_shares_to(buyer, self.athlete, volume)
        # buyer.save()
        # seller.save()

        trade = Trade(
            athlete=self.athlete,
            volume=volume,
            buyer=buyer,
            seller=seller,
            unit_price=matched_price,
        )
        trade.save()
        LOGGER.info("Created trade: %s", trade)
