from django.db import models
from .asset import Asset
from .entity import Entity
from .athlete import Athlete

class Offer(models.Model):
    """
    Offer to buy or sell something
    """

    BUY = "B"
    SELL = "S"
    TYPES = ((BUY, "Buy"), (SELL, "Sell"))

    OPEN = "O"
    FULFILLED = "F"
    CANCELLED = "C" # maybe just delete the offer instead?
    STATUSES = (
        (OPEN, "Open"),
        (FULFILLED, "Fulfilled"),
        (CANCELLED, "Cancelled")
    )

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    unit_price = models.DecimalField(decimal_places=2, max_digits=10)
    buy_sell = models.CharField(max_length=1, choices=TYPES, default=BUY)
    status = models.CharField(max_length=1, choices=STATUSES, default=OPEN)

    def __repr__(self):
        return f"{self.buy_sell}/{self.athlete},{self.volume}/{self.unit_price}/{self.status}"

    def __str__(self):
        return self.__repr__()

    def save(self, *args, **kwargs):
        self.unit_price = round(self.unit_price, 2)
        self.volume = round(self.volume, 2)
        super(Offer, self).save(*args, **kwargs)

    