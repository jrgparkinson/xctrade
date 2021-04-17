from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trading.athlete import Athlete, Club
from trading.entity import User, Entity, get_cowley_club_bank
from trading.order import Order, Trade
from trading.asset import Share
from trading.races import Result, Race, compute_dividends, Dividend
from trading.auction import Auction, Bid
from trading.loan import Loan, apply_all_interest, LoanPolicy
import json
from decimal import Decimal
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import logging
import random
import pytz
from datetime import timedelta, datetime

LOGGER = logging.getLogger(__name__)


class LoanTests(APITestCase):
    loans_url = "/api/loans/"

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
            Token.objects.create(user=user)

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

        # Create loan policy
        LoanPolicy(lender=get_cowley_club_bank(), interest_interval=timedelta(days=7), interest_rate=0.05, max_balance=1000).save()

    def test_create_loan(self):

        loan_policy = LoanPolicy.objects.get(pk=1)

        # lender = get_cowley_club_bank()
        # recipient = Entity.objects.get(name="jparkinson")

        token = Token.objects.get(user__username="jparkinson")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # Try and create a loan
        response = client.post(
            self.loans_url, [{"balance": 100.0, "loan_info_id": loan_policy.pk}], format="json",
        )
        LOGGER.info(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        loans = Loan.objects.all()
        self.assertEqual(len(loans), 1)

        # Now add another, and update the first
        response = client.get(self.loans_url)
        loans = json.loads(response.content)
        LOGGER.info(loans)
        self.assertEqual(len(loans), 1)
        self.assertEqual(loans[0]["balance"], "100.00")
        self.assertEqual(loans[0]["loan_info"]["interest_rate"], "0.05")
        self.assertIsNone(loans[0]["interest_last_added"])
        self.assertEqual(
            float(Entity.objects.get(name="jparkinson").capital),
            Entity.INITIAL_CAPITAL + 100.0,
        )

        # Repay $15
        pk = loans[0]["pk"]
        response = client.put(
            f"{self.loans_url}{pk}/", {"balance": 85.0}, format="json",
        )

        self.assertEqual(Loan.objects.get(pk=pk).balance, 85)
        self.assertEqual(
            float(Entity.objects.get(name="jparkinson").capital),
            Entity.INITIAL_CAPITAL + 85.0,
        )

    def test_accrue_interest(self):
        # lender = get_cowley_club_bank()
        recipient = Entity.objects.get(name="jparkinson")

        loan_policy = LoanPolicy.objects.get(pk=1)

        loan = Loan.objects.create(loan_info=loan_policy, recipient=recipient, balance=Decimal(10.0))
        loan.created=datetime.now(pytz.utc)-timedelta(days=4)

        # Not enough time passed, don't accrue interest
        loan.accrue_interest()
        self.assertEqual(loan.balance, 10.0)

        loan.created=datetime.now(pytz.utc)-timedelta(days=8)
        loan.accrue_interest()
        self.assertEqual(loan.balance, 10.5)

        # Apply again, shouldn't change anything
        loan.accrue_interest()
        self.assertEqual(loan.balance, 10.5)


        # add a new loan
        loan2 = Loan.objects.create(loan_info=loan_policy, recipient=recipient, balance=20.0,
                                    interest_last_added = datetime.now(pytz.utc) - timedelta(days=8))

        apply_all_interest()
        self.assertEqual(loan.balance, 10.5)
        self.assertEqual(Loan.objects.get(pk=loan2.pk).balance, 21.0)
