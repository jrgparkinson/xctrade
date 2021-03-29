from .athlete import Athlete
from .exceptions import TradingException
from .entity import Entity
from django.db import models
import logging
from decimal import Decimal
from .equations import get_equation

LOGGER = logging.getLogger(__name__)


class Race(models.Model):
    """ Many races per event """

    # event = models.ForeignKey(
    #     Event, related_name="%(app_label)s_%(class)s_event", on_delete=models.CASCADE
    # )
    name = models.CharField(max_length=100)
    time = models.DateTimeField()
    results_link = models.URLField(blank=True, null=True)
    event_details_link = models.URLField(blank=True, null=True)
    max_dividend = models.DecimalField(max_digits=10, decimal_places=2)
    min_dividend = models.DecimalField(max_digits=10, decimal_places=2, default=10.0)
    num_competitors = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.time.strftime("%d/%m/%Y %H:%m"))

    @property
    def has_results(self):
        return len(self.result_set.all()) > 0

    def compute_dividends(self):
        results = Result.objects.all().filter(race=self)

        # Perform some checks
        if len(results) == 0:
            return "No results uploaded yet for this race"

        if not self.num_competitors or self.num_competitors == 0:
            return "Number of competitors for this race hasn't been entered."

        # Now actually compute dividends
        compute_dividends(self)

        return None

    def distribute_dividends(self):
        results = Result.objects.all().filter(race=self)
        if len(results) == 0:
            return "No results uploaded yet for this race"

        # Check dividends have been computed
        for r in results:
            if not r.dividend:
                return "Dividends have not been computed for a competitor in this race: {}".format(
                    r.athlete.name
                )

        # Now distribute
        for r in results:
            for i in Entity.objects.all():
                vol_owned = i.vol_owned(r.athlete)
                if float(vol_owned) == 0:
                    continue

                # dividend_earned = vol_owned * r.dividend

                try:
                    # bank = cowley_club_bank()
                    # bank.transfer_cash_to(
                    #     dividend_earned, i, reason="Dividend payment {}".format(r.id)
                    # )
                    Dividend(
                        result=r,
                        volume=vol_owned,
                        entity=i,
                        dividend_per_share=r.dividend,
                    ).save()
                    # i.capital += dividend_earned

                    # TODO: create a record of this dividend payment

                    r.dividend_distributed = True
                    r.save()
                    # i.save()

                except TradingException as e:
                    return "{}: {}".format(e.title, e.desc)

        return None


class Result(models.Model):
    """ Results are recorded for athletes when they
    perform well in an event.

    They are entered manually by the XChange administrator, and automatically distributed 
    in a proportional manner to those
    who owned shares in the athlete at the start of the event. 
    """

    athlete = models.ForeignKey(
        Athlete,
        related_name="%(app_label)s_%(class)s_athlete",
        on_delete=models.CASCADE,
    )
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    position = models.IntegerField()
    time = models.DurationField(null=True, blank=True)
    dividend = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    dividend_distributed = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            "race",
            "athlete",
        )

    def __str__(self):
        return "{}. {} ({})".format(self.position, self.athlete.name, self.race.name)


def compute_dividends(race: Race):
    if not race.num_competitors:
        return

    results = Result.objects.all().filter(race=race)

    eq = get_equation("dividend")

    d_min = race.min_dividend
    d_max = race.max_dividend
    num_comp = race.num_competitors

    for r in results:
        position = r.position

        # Using eval because this is trusted (not user input)
        r.dividend = eval(eq)
        # LOGGER.info(r.dividend)
        # scaled_position = (
        #     race.num_competitors - (r.position - 1)
        # ) / race.num_competitors
        # r.dividend =  race.min_dividend + (race.max_dividend - race.min_dividend) * pow(scaled_position, 2),

        r.save()


class Dividend(models.Model):
    """ To track a dividend payment """

    result = models.ForeignKey(
        Result, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_result",
    )
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dividend_per_share = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # In case we need to revert the payment
    reverted = models.BooleanField(default=False)

    @property
    def total_dividend(self):
        return Decimal(self.volume * self.dividend_per_share)

    def pay(self):
        self.entity.capital += self.total_dividend
        self.reverted = False
        self.entity.save()

    def revert(self):
        self.entity.capital -= self.total_dividend
        self.reverted = True
        self.entity.save()
