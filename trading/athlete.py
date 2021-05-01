import pytz
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import models
from django.apps import apps
from django.db.models import Q

LOGGER = logging.getLogger(__name__)

class Club(models.Model):
    """ Club model """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Athlete(models.Model):
    """
    An athlete who earns dividends for their share holders
    """

    VALUE_AVERAGE_SIZE = 3

    name = models.CharField(max_length=100, unique=True)
    power_of_10 = models.URLField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_value(self, time):
        """ Compute the value of an athlete """
        Trade = apps.get_model("trading.Trade")
        recent_trades = (
            Trade.objects.all()
            .filter(Q(athlete=self) & Q(timestamp__lte=time) & Q(future=None))
            .order_by("-timestamp")
        )
        if recent_trades:
            # Volume average all trades in last week, if any
            trades_in_last_week = [t for t in recent_trades if t.timestamp > datetime.now(pytz.utc) - timedelta(days=7)]
            if trades_in_last_week:
                price_vol_sum = sum([t.unit_price * t.volume for t in trades_in_last_week])
                vol_sum = sum([t.volume for t in trades_in_last_week])
                value = round(price_vol_sum/vol_sum, 2)
                # LOGGER.info(trades_in_last_week)
                # LOGGER.info(f"sum(price*vol)={price_vol_sum}, sum(vol) = {vol_sum}, value={value}")
                return value
            else:
                # If no trades in last week, just take most recent value
                return recent_trades[0].unit_price
        else:
            return None

    @property
    def prev_value(self):
        return self.get_value(datetime.now(pytz.utc) - timedelta(days=7))

    @property
    def percent_change(self):
        if self.value and self.prev_value:
            return round(100.0 * float((self.value - self.prev_value) / self.value), 2)
        return None

    @property
    def value(self):
        """
        Value = volume weighted sum of last 2 trades
        """
        return self.get_value(datetime.now(pytz.utc))

    @property
    def weekly_volume(self):
        """ Sum volume of all trades for athlete in past week"""
        Trade = apps.get_model("trading.Trade")
        one_week_ago = datetime.now(pytz.utc) - timedelta(weeks=1)
        recent_trades = Trade.objects.all().filter(
            Q(athlete=self) & Q(timestamp__gte=one_week_ago) & Q(future=None)
        )
        total_volume = sum([t.volume for t in recent_trades])
        # LOGGER.info("Volume: %s", total_volume)
        return total_volume
