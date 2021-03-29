from django.core.management.base import BaseCommand
from trading.models import Athlete, Club, Offer, Entity, Share
import random

class Command(BaseCommand):
    help = "Populate database"

    def handle(self, *args, **kwargs):
        ouccc, created = Club.objects.get_or_create(name="OUCCC")
        Club.objects.get_or_create(name="CUHH")

        entities = []
        for entity in ("jparkinson", "lcotter", "mweatherseed", "jwoods"):
            entity, created = Entity.objects.get_or_create(name=entity)
            entities.append(entity)

        for athlete in ("Jamie Parkinson",
            "Luke Cotter",
            "Miles Weatherseed",
            "Joseph Woods",
            "Jack Millar",
            "Noah Hurton",
            "Oliver Paulin"):
            athlete, created = Athlete.objects.get_or_create(name=athlete, club=ouccc)

            # share, created = Share.objects.get_or_create(athlete=athlete, volume=random.random())

            offer, created = Offer.objects.get_or_create(athlete=athlete, volume=random.random(), entity=random.choice(entities),
            unit_price=random.random(), buy_sell=random.choice(Offer.TYPES)[0])
            print(offer)