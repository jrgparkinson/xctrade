from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trading.athlete import Athlete, Club
from trading.entity import User, Entity, get_cowley_club_bank
from trading.order import Order
from trading.asset import Share
from trading.races import Result, Race, compute_dividends, Dividend
from trading.auction import Auction, Bid
import json
from decimal import Decimal
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import logging
import random
from datetime import timedelta, datetime

LOGGER = logging.getLogger(__name__)


class DividendTests(APITestCase):
    auction_url = "/api/auction/"
    bids_url = "/api/bids/"

    def setUp(self):
        ouccc, created = Club.objects.get_or_create(name="OUCCC")
        Club.objects.get_or_create(name="CUHH")

        bank = get_cowley_club_bank()

        users = []
        for name in ("jparkinson", "lcotter", "mweatherseed", "jwoods"):
            user, created = User.objects.get_or_create(
                username=name, password="password"
            )
            user.entity.name = name
            user.entity.save()
            users.append(user)
            token = Token.objects.create(user=user)

        for athlete in (
            "Jamie Parkinson",
            "Luke Cotter",
            "Miles Weatherseed",
            "Joseph Woods",
            "Jack Millar",
            "Noah Hurton",
            "Oliver Paulin",
        ):
            athlete, created = Athlete.objects.get_or_create(name=athlete, club=ouccc)

            Share(athlete=athlete, volume=Decimal(2), owner=bank).save()

        # Create auction
        Auction(
            name="Test",
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            bank=bank,
        ).save()

    def test_auction(self):

        auction = Auction.get_active_auction()
        self.assertEqual(auction.name, "Test")

        token = Token.objects.get(user__username="jparkinson")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # Try and create a bid
        response = client.post(
            f"/api/bids/{auction.pk}/",
            [
                {
                    "athlete": 1,
                    "auction": auction.pk,
                    "volume": 2.0,
                    "price_per_volume": 10.0,
                }
            ],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bid.objects.count(), 1)

        # Now add another, and update the first
        response = client.post(
            f"/api/bids/{auction.pk}/",
            [
                {
                    "athlete": 1,
                    "auction": auction.pk,
                    "volume": 2.0,
                    "price_per_volume": 2.0,
                },
                {
                    "athlete": 2,
                    "auction": auction.pk,
                    "volume": 1.0,
                    "price_per_volume": 3.0,
                },
            ],
            format="json",
        )
        bids = Bid.objects.all()
        self.assertEqual(len(bids), 2)

        response = client.get(f"/api/bids/{auction.pk}/")
        LOGGER.info(json.loads(response.content))
        self.assertEqual(
            json.loads(response.content),
            [
                {
                    "pk": 2,
                    "status": "P",
                    "bidder": {
                        "pk": 2,
                        "name": "jparkinson",
                        "user": 2,
                        "capital": "1000.00",
                        "portfolio_value": 1000.0,
                    },
                    "auction": 1,
                    "athlete": 1,
                    "volume": "2.00",
                    "price_per_volume": "2.00",
                },
                {
                    "pk": 3,
                    "status": "P",
                    "bidder": {
                        "pk": 2,
                        "name": "jparkinson",
                        "user": 2,
                        "capital": "1000.00",
                        "portfolio_value": 1000.0,
                    },
                    "auction": 1,
                    "athlete": 2,
                    "volume": "1.00",
                    "price_per_volume": "3.00",
                },
            ],
        )
