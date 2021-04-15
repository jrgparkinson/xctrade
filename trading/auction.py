from datetime import datetime
from django.db import models
from django.db.models import Q
import logging
from rest_framework.exceptions import APIException
from .entity import Entity
from .athlete import Athlete
from .asset import Share
from .exceptions import TradingException
from .order import Trade
import pytz

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
        now = datetime.now(pytz.utc)
        auctions = Auction.objects.all().filter(
            Q(start_date__lte=now) & Q(end_date__gte=now)
        )

        LOGGER.info("Auctions: %s" % auctions)

        if len(auctions) > 1:
            raise MultipleCurrentAuctionsError
        elif len(auctions) == 1:
            return auctions[0]

        return None

    def settle_bids(self):
        if self.end_date > datetime.now(pytz.utc):
            raise TradingException("Auction hasn't finished yet: {}".format(self.name))
        else:
            # Process bids from highest to smallest price per volume
            bids = (
                Bid.objects.all()
                .filter(auction=self, status=Bid.PENDING)
                .order_by("-price_per_volume")
            )

            for bid in bids:

                # Skip bids for no shares
                if bid.volume == 0:
                    continue

                bank_share_vol = self.bank.vol_owned(bid.athlete)
                if bank_share_vol == 0:
                    continue

                try:
                    # try making and executing trade
                    # if there are any issues e.g. insufficient shares, funds, then trade will
                    # fail and we ignore the exception then move on to the next one

                    vol = min(bank_share_vol, bid.volume)

                    Trade(
                        athlete=bid.athlete,
                        volume=vol,
                        buyer=bid.bidder,
                        seller=self.bank,
                        unit_price=bid.price_per_volume,
                    ).save()

                    bid.status = Bid.ACCEPTED
                    bid.save()
                    print("Accepted bid: {}".format(bid))
                except APIException as e:
                    bid.status = Bid.REJECTED
                    bid.save()
                    print("Could not accept bid: {} due to: {}".format(bid, e))
                    # print(e)


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
        unique_together = (
            "bidder",
            "athlete",
        )

    def __str__(self):
        return f"Bid for {self.athlete.name} ({self.volume} @ {self.price_per_volume}) by {self.bidder.name}"
