from django.core.management.base import BaseCommand
from trading.models import Athlete, Club, Order, Entity, Share
from django.contrib.auth.models import User
import random
import logging
import traceback
from trading.exceptions import InvalidOrderException
from datetime import datetime, timedelta

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Populate database"

    def handle(self, *args, **kwargs):
        ouccc, created = Club.objects.get_or_create(name="OUCCC")
        Club.objects.get_or_create(name="CUHH")

        entities = []
        for name in ("jparkinson", "lcotter", "mweatherseed", "jwoods"):
            user, created = User.objects.get_or_create(username=name, password="password")
            user.entity.name = name
            user.entity.save()
            entities.append(user.entity)
            Share.objects.all().filter(owner=user.entity).delete()

        for athlete in ("Jamie Parkinson",
            "Luke Cotter",
            "Miles Weatherseed",
            "Joseph Woods",
            "Jack Millar",
            "Noah Hurton",
            "Oliver Paulin",
            "Dan Bundred",
            "Tom Wood"):
            athlete, created = Athlete.objects.get_or_create(name=athlete, club=ouccc)

            for entity in entities:
                
                share = entity.get_share(athlete)
                share.volume = 5.0
                share.save()

                # Share.objects.get_or_create(athlete=athlete, volume=5.0, owner=entity)

            # share, created = Share.objects.get_or_create(athlete=athlete, volume=random.random())

            for _ in range(10):
                try:
                    order, created = Order.objects.get_or_create(athlete=athlete, volume=random.random(),
                    entity=random.choice(entities),
                    unit_price=random.random(), buy_sell=random.choice(Order.TYPES)[0])
                    print(order)
                except InvalidOrderException as e:
                    LOGGER.info(e)
                    # traceback.print_exc()
                    
                # create some fake past trades
                buyer = random.choices(entities)
                seller = random.choices(entities)
                while buyer == seller:
                    seller = random.choices(entities)
                t = Trade(athlete=athlete,
                      volume=random.random(),
                      unit_price=random.random(),
                      buyer=buyer,
                      seller=seller)
                t.save()
                t.timestamp=datetime.now()-timedelta(days=20*random.random())
                t.save()