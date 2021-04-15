from datetime import datetime
from django.db import models
from django.db.models import Q
import logging
from rest_framework.exceptions import APIException
from .entity import Entity
from .athlete import Athlete
from .asset import Share

LOGGER = logging.getLogger(__name__)

class MultipleCurrentAuctionsError(APIException):
    status_code = 500
    default_detail = "Multiple current auctions."
    default_code = "multiple_auctions"


class Auction(models.Model):
    """ Auction is where a bank sells off all it's shares """
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    bank = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def __str__(self):
        return "{} (Ends: {})".format(self.name, self.end_date)

    def available_shares(self):
        """ Shares available in this auction """
        shares = Share.objects.all().filter(owner=self.bank)
        LOGGER.info("Bank shares: %s" % shares)
        return shares

    @staticmethod
    def get_active_auction():
        now = datetime.now()
        auctions = Auction.objects.all().filter(Q(start_date__lte=now) & Q(end_date__gte=now))

        LOGGER.info("Auctions: %s" % auctions)

        if len(auctions) > 1:
            raise MultipleCurrentAuctionsError
        elif len(auctions) == 1:
            return auctions[0]
        
        return None


class Bid(models.Model):
    PENDING = "P"
    ACCEPTED = "A"
    REJECTED = "R"
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    )

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    bidder = models.ForeignKey(
        Entity, related_name="%(app_label)s_%(class)s_bidder", on_delete=models.CASCADE
    )
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_volume = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        # Each bidder can only have one bid on one athlete
        unique_together = ('bidder', 'athlete',)

