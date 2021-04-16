from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trading.athlete import Athlete, Club
from trading.entity import User, Entity, get_cowley_club_bank
from trading.order import Order, Trade
from trading.asset import Share
from trading.races import Result, Race, compute_dividends, Dividend
from trading.auction import Auction, Bid
import json
from decimal import Decimal
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import logging
import random
import pytz
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
            start_date=datetime.now(pytz.utc) - timedelta(days=1),
            end_date=datetime.now(pytz.utc) + timedelta(days=1),
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
        bids = json.loads(response.content)
        self.assertEqual(float(bids[0]["volume"]), 2.0)
        self.assertEqual(float(bids[0]["price_per_volume"]), 2.0)
        self.assertEqual(float(bids[1]["volume"]), 1.0)
        self.assertEqual(float(bids[1]["price_per_volume"]), 3.0)

    def test_auction_settled(self):
        """ Test settling an auction """
        auction = Auction.get_active_auction()

        # entities = Entity.objects.all()

        player_jp = Entity.objects.get(name="jparkinson")
        player_lc = Entity.objects.get(name="lcotter")

        athlete_parkinson = Athlete.objects.get(name="Jamie Parkinson")
        athlete_cotter = Athlete.objects.get(name="Luke Cotter")
        athlete_weatherseed = Athlete.objects.get(name="Miles Weatherseed")

        # Bank has 2 shares in every athlete, set up some bids

        # player a should get the shares luke cotter
        Bid(
            athlete=athlete_cotter,
            bidder=player_jp,
            volume=3,
            price_per_volume=2.0,
            auction=auction,
        ).save()
        Bid(
            athlete=athlete_cotter,
            bidder=player_lc,
            volume=2,
            price_per_volume=1.9,
            auction=auction,
        ).save()

        # player a should get all 1.5 shares, b should get 0.5 shares
        Bid(
            athlete=athlete_parkinson,
            bidder=player_jp,
            volume=1.5,
            price_per_volume=1.5,
            auction=auction,
        ).save()
        Bid(
            athlete=athlete_parkinson,
            bidder=player_lc,
            volume=2,
            price_per_volume=1.4,
            auction=auction,
        ).save()

        # Should both get 1 share each
        Bid(
            athlete=athlete_weatherseed,
            bidder=player_jp,
            volume=1,
            price_per_volume=1.0,
            auction=auction,
        ).save()
        Bid(
            athlete=athlete_weatherseed,
            bidder=player_lc,
            volume=1,
            price_per_volume=0.9,
            auction=auction,
        ).save()

        # Settle auction
        self.assertEqual(len(Trade.objects.all()), 0)
        auction.end_date = datetime.now(pytz.utc) - timedelta(minutes=1)
        auction.settle_bids()

        trades = Trade.objects.all()
        for t in trades:
            LOGGER.info(t)

        self.assertEqual(len(trades), 5)

        # Check shares
        Share.objects.get(athlete=athlete_cotter, owner=player_jp, volume=2)

        Share.objects.get(athlete=athlete_parkinson, owner=player_jp, volume=1.5)
        Share.objects.get(athlete=athlete_parkinson, owner=player_lc, volume=0.5)

        Share.objects.get(athlete=athlete_weatherseed, owner=player_jp, volume=1)
        Share.objects.get(athlete=athlete_weatherseed, owner=player_lc, volume=1)

        # Check capital
        self.assertEqual(
            float(Entity.objects.get(name="jparkinson").capital),
            Entity.INITIAL_CAPITAL - (4 + 1.5 * 1.5 + 1),
        )
        self.assertEqual(
            float(Entity.objects.get(name="lcotter").capital),
            Entity.INITIAL_CAPITAL - (0.5 * 1.4 + 0.9),
        )
