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
        Trade = apps.get_model('trading.Trade')
        recent_trades = Trade.objects.all().filter(Q(athlete=self) & Q(timestamp__lte=time)).order_by('-timestamp')
        if recent_trades:
            return recent_trades[0].unit_price
        else:
            return None

    @property
    def prev_value(self):
        return self.get_value(datetime.now() - timedelta(days=7))
        
    @property
    def percent_change(self):
        return 100.0*(self.value-self.prev_value)/self.value

    @property
    def value(self):
        Trade = apps.get_model('trading.Trade')
        recent_trades = Trade.objects.all().filter(athlete=self).order_by('-timestamp')
        if recent_trades:
            return recent_trades[0].unit_price
        else:
            return None