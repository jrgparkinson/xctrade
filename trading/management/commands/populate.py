from django.core.management.base import BaseCommand
from trading.models import Athlete, Club, Order, Entity, Share, Trade, Race, Result, LoanPolicy, Future
from trading.entity import get_cowley_club_bank
from django.contrib.auth.models import User
import random
import logging
from decimal import Decimal
import traceback
from trading.exceptions import InvalidOrderException
from datetime import datetime, timedelta
import pytz

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate database"

    def handle(self, *args, **kwargs):
        ouccc, created = Club.objects.get_or_create(name="OUCCC")
        Club.objects.get_or_create(name="CUHH")

        entities = []
        for name in ("jparkinson", "lcotter", "mweatherseed", "jwoods"):
            user, created = User.objects.get_or_create(
                username=name, password="password"
            )
            user.entity.name = name
            user.entity.save()
            entities.append(user.entity)
            Share.objects.all().filter(owner=user.entity).delete()

        Order.objects.all().delete()
        Trade.objects.all().delete()

        for athlete in (
            "Jamie Parkinson",
            "Luke Cotter",
            "Miles Weatherseed",
            "Joseph Woods",
            "Jack Millar",
            "Noah Hurton",
            "Oliver Paulin",
            "Dan Bundred",
            "Tom Wood",
        ):
            athlete, created = Athlete.objects.get_or_create(name=athlete, club=ouccc)

            for entity in entities:
                share = entity.get_share(athlete)
                share.volume = 5.0
                share.save()

            # share, created = Share.objects.get_or_create(athlete=athlete, volume=random.random())

            price = random.random()
            for _ in range(3):
                try:
                    order, created = Order.objects.get_or_create(
                        athlete=athlete,
                        volume=random.random(),
                        entity=random.choice(entities),
                        unit_price=random.random(),
                        buy_sell=random.choice(Order.TYPES)[0],
                    )
                    print(order)
                except InvalidOrderException as e:
                    LOGGER.info(e)
                    # traceback.print_exc()
            for _ in range(10):
                # create some fake past trades
                buyer = random.choice(entities)
                seller = random.choice(entities)
                while buyer == seller:
                    seller = random.choice(entities)

                price = price + 0.1 * random.random()
                t = Trade(
                    athlete=athlete,
                    volume=random.random(),
                    unit_price=price,
                    buyer=buyer,
                    seller=seller,
                )
                t.save()
                t.timestamp = datetime.now(pytz.utc) - timedelta(
                    days=20 * random.random()
                )
                t.save()

        # Create some races
        mens_blues, _ = Race.objects.get_or_create(
            name="Varsity XC Men's Blues",
            time=datetime(2021, 2, 1, 14, 0, tzinfo=pytz.utc),
            max_dividend=100,
            min_dividend=10,
        )
        womens_blues, _ = Race.objects.get_or_create(
            name="Varsity XC Women's Blues",
            time=datetime(2021, 2, 1, 15, 0, tzinfo=pytz.utc),
            max_dividend=100,
            min_dividend=10,
        )
        mens_twos, _ = Race.objects.get_or_create(
            name="Varsity XC Men's II",
            time=datetime(2021, 2, 1, 16, 0, tzinfo=pytz.utc),
            max_dividend=50,
            min_dividend=1,
        )

        # Future races
        mens_cuppers, _ = Race.objects.get_or_create(
            name="Cuppers (men)",
            time=datetime(2021, 10, 20, 11, 0, tzinfo=pytz.utc),
            max_dividend=40,
            min_dividend=1,
        )

        # Some results
        Result.objects.all().delete()
        time = timedelta(minutes=30, seconds=0)
        for position, athlete in enumerate(Athlete.objects.all()):
            pos = position + 1
            time = time + timedelta(seconds=random.randint(1, 30))
            Result.objects.get_or_create(
                athlete=athlete, position=pos, time=time, race=mens_blues
            )

        # Setup bank shares
        bank = get_cowley_club_bank()
        Share.objects.all().filter(owner=bank).delete()
        for athlete in Athlete.objects.all():
            share = bank.get_share(athlete)
            share.volume = Decimal(100.0)
            share.save()

        LoanPolicy.objects.get_or_create(lender=bank, interest_rate=0.05, interest_interval=timedelta(days=7), max_balance=1000)
        LoanPolicy.objects.get_or_create(lender=bank, interest_rate=0.1, interest_interval=timedelta(days=7), max_balance=10000)

        # Some futures markets
        Future.objects.get_or_create(expires=datetime(2021, 12, 1, tzinfo=pytz.utc), closes=datetime(2021, 10, 1, tzinfo=pytz.utc)))
        Future.objects.get_or_create(expires=datetime(2021, 11, 1, tzinfo=pytz.utc), closes=datetime(2021, 9, 1, tzinfo=pytz.utc)))
        Future.objects.get_or_create(expires=datetime(2021, 10, 1, tzinfo=pytz.utc), closes=datetime(2020, 10, 1, tzinfo=pytz.utc)))