from django.db import models
from django.apps import apps
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Q


class Club(models.Model):
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
        Trade = apps.get_model("trading.Trade")
        recent_trades = (
            Trade.objects.all()
            .filter(Q(athlete=self) & Q(timestamp__lte=time))
            .order_by("-timestamp")
        )
        if recent_trades:
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
        Trade = apps.get_model("trading.Trade")
        recent_trades = Trade.objects.all().filter(athlete=self).order_by("-timestamp")
        if recent_trades:
            if len(recent_trades) == 1:
                return recent_trades[0].unit_price
            else:
                NUM_TRADES = 2  # consider N most recent trades
                trades_to_consider = recent_trades[:NUM_TRADES]
                total_vol = Decimal(0)
                total_vol_price = Decimal(0)
                for t in trades_to_consider:
                    total_vol_price += t.unit_price * t.volume
                    total_vol += t.volume

                return round(total_vol_price / total_vol, 2)

        else:
            return None

    @property
    def weekly_volume(self):
        """ Sum volume of all trades for athlete in past week"""
        Trade = apps.get_model("trading.Trade")

        one_week_ago = datetime.now(pytz.utc) - timedelta(weeks=1)
        recent_trades = Trade.objects.all().filter(
            Q(athlete=self) & Q(timestamp__gte=one_week_ago)
        )
        total_volume = sum([t.volume for t in recent_trades])
        # LOGGER.info("Volume: %s", total_volume)
        return total_volume
