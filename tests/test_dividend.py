
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trading.athlete import Athlete, Club
from trading.entity import User, Entity
from trading.order import Order
from trading.asset import Share
from trading.races import Result, Race, compute_dividends, Dividend
import json
from decimal import Decimal
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import logging
import random
from datetime import timedelta, datetime

LOGGER = logging.getLogger(__name__)

class DividendTests(APITestCase):
    url = "/api/orders/"

    def setUp(self):
        ouccc, created = Club.objects.get_or_create(name="OUCCC")
        Club.objects.get_or_create(name="CUHH")

        users = []
        for name in ("jparkinson", "lcotter", "mweatherseed", "jwoods"):
            user, created = User.objects.get_or_create(username=name,password="password")
            user.entity.name = name
            user.entity.save()
            users.append(user)
            token = Token.objects.create(user=user)

        for athlete in ("Jamie Parkinson",
            "Luke Cotter",
            "Miles Weatherseed",
            "Joseph Woods",
            "Jack Millar",
            "Noah Hurton",
            "Oliver Paulin"):
            athlete, created = Athlete.objects.get_or_create(name=athlete, club=ouccc)

            for user in users:
                Share(athlete=athlete, volume=Decimal(2), owner=user.entity).save()

        # Create race and results
        race, created = Race.objects.get_or_create(name="Race", time=datetime.now(), min_dividend=10, max_dividend=100)

        Result.objects.all().filter(race=race).delete()

    def test_compute_dividend(self):
        race = Race.objects.get(pk=1)
        race.num_competitors = 10

        # Setup positions and expected dividends
        expected_results = {"Jamie Parkinson": (1, Decimal(100)),
            "Luke Cotter": (5, Decimal(60)),
            "Miles Weatherseed": (10, Decimal(10))}

        time = timedelta(minutes=30)
        for athlete, result in expected_results.items():
            ath = Athlete.objects.get(name=athlete)

            Result.objects.create(athlete=ath, time=time, race=race, position=result[0])
            time = time + timedelta(seconds=random.randint(1, 60))

        
        compute_dividends(race)   

        results = Result.objects.all().filter(race=race)

        # LOGGER.info(results)
        dividends = {}
        for result in results:
            self.assertEqual(result.dividend, expected_results[result.athlete.name][1]) 
            self.assertFalse(result.dividend_distributed)
        

        # Distribute dividend
        race.distribute_dividends()

        # Check whoever owned shares got paid
        jparkinson = Entity.objects.get(name="jparkinson")
        self.assertEqual(
            Entity.objects.get(name="jparkinson").capital,
            1000 + 2*(100 + 60 + 10)
        )

        # Check dividend objects exist for each user/athlete combo
        dividends = Dividend.objects.all().filter(result__race=race)
        self.assertEqual(len(dividends), 3*4)

        # Test reverting
        for dividend in dividends.filter(entity=jparkinson):
            dividend.revert()

        self.assertEqual(
            Entity.objects.get(name="jparkinson").capital,
            1000
        )

        self.assertEqual(
            Entity.objects.get(name="jwoods").capital,
            1000 + 2*(100 + 60 + 10)
        )
        