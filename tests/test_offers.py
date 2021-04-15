from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trading.athlete import Athlete, Club
from trading.entity import User, Entity, get_cowley_club_bank
from trading.order import Order, Trade
from trading.asset import Share
import json
from decimal import Decimal
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import logging

LOGGER = logging.getLogger(__name__)


class AthletesTests(APITestCase):
    def test_get_athletes(self):
        """
        Ensure we can get a list of athletes
        """
        response = self.client.get("/api/athletes/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), [])


class OrdersTests(APITestCase):
    url = "/api/orders/"

    def setUp(self):
        ouccc, created = Club.objects.get_or_create(name="OUCCC")
        Club.objects.get_or_create(name="CUHH")

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

            for user in users:
                Share(athlete=athlete, volume=10, owner=user.entity).save()

    def test_create_orders(self):

        data = {
            "athlete_id": 4,
            "volume": "0.99",
            "unit_price": "0.99",
            "buy_sell": "B",
        }

        token = Token.objects.get(user__username="jparkinson")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        response = client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        response = client.get(self.url, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 1)
        json_resp_order = json_response[0]
        self.assertEqual(json_resp_order["athlete"]["pk"], 4)
        self.assertEqual(json_resp_order["entity"]["pk"], 1)
        self.assertEqual(json_resp_order["status"], "O")
        self.assertEqual(json_resp_order["buy_sell"], "B")
        self.assertEqual(json_resp_order["unit_price"], "0.99")
        self.assertEqual(json_resp_order["volume"], "0.99")

        # Now add another order from someone else, check it's actioned
        client.credentials(
            HTTP_AUTHORIZATION="Token "
            + Token.objects.get(user__username="lcotter").key
        )

        response = client.post(
            self.url,
            {"athlete_id": 4, "volume": "0.2", "unit_price": "0.95", "buy_sell": "S"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)

        order_buyer = Order.objects.get(entity__user__username="jparkinson")
        order_seller = Order.objects.get(entity__user__username="lcotter")
        self.assertEqual(order_buyer.unfilled_volume, Decimal("0.79"))
        self.assertEqual(order_buyer.status, "O")
        self.assertEqual(order_seller.unfilled_volume, Decimal("0.0"))
        self.assertEqual(order_seller.status, "F")

        share_buyer = Share.objects.get(
            owner__user__username="jparkinson", athlete__name="Joseph Woods"
        )
        share_seller = Share.objects.get(
            owner__user__username="lcotter", athlete__name="Joseph Woods"
        )

        self.assertEqual(share_buyer.volume, Decimal("10.2"))
        self.assertEqual(share_seller.volume, Decimal("9.8"))

        # Price should be 0.2*(0.95+0.99)/2 = 0.194 = 0.19
        buyer = Entity.objects.get(user__username="jparkinson")
        seller = Entity.objects.get(user__username="lcotter")
        self.assertEqual(buyer.capital, Decimal("999.81"))
        self.assertEqual(seller.capital, Decimal("1000.19"))

        athlete = Athlete.objects.get(name="Joseph Woods")
        self.assertEqual(athlete.value, Decimal("0.97"))

        # Add another sell trade, check it is also actioned
        response = client.post(
            self.url,
            {"athlete_id": 4, "volume": "0.1", "unit_price": "0.9", "buy_sell": "S"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 3)
        share_buyer = Share.objects.get(
            owner__user__username="jparkinson", athlete__name="Joseph Woods"
        )
        share_seller = Share.objects.get(
            owner__user__username="lcotter", athlete__name="Joseph Woods"
        )
        self.assertEqual(share_buyer.volume, Decimal("10.3"))
        self.assertEqual(share_seller.volume, Decimal("9.7"))

        # Price should be 0.1*(0.9+0.99)/2 = 0.09
        buyer = Entity.objects.get(user__username="jparkinson")
        seller = Entity.objects.get(user__username="lcotter")
        self.assertEqual(buyer.capital, Decimal("999.72"))
        self.assertEqual(seller.capital, Decimal("1000.28"))

        athlete = Athlete.objects.get(name="Joseph Woods")
        self.assertEqual(athlete.value, Decimal("0.96"))

        # Add a sell trade that's too expensive, shouldn't be actioned
        response = client.post(
            self.url,
            {"athlete_id": 4, "volume": "0.1", "unit_price": "1.9", "buy_sell": "S"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 4)
        order_seller = Order.objects.get(
            entity__user__username="lcotter", unit_price=Decimal("1.9")
        )
        self.assertEqual(order_seller.unfilled_volume, Decimal("0.1"))
        self.assertEqual(order_seller.status, "O")

        # Add a sell trade for more shares than owned, shouldn't be created
        response = client.post(
            self.url,
            {"athlete_id": 4, "volume": "20", "unit_price": "0.6", "buy_sell": "S"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 4)

        # Buy trade for more money than we have, shouldn't be created
        response = client.post(
            self.url,
            {"athlete_id": 4, "volume": "20", "unit_price": "100000", "buy_sell": "B"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 4)

    def test_cancel_order(self):
        token = Token.objects.get(user__username="jparkinson")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # Create order
        data = {
            "athlete_id": 4,
            "volume": "0.99",
            "unit_price": "0.99",
            "buy_sell": "B",
        }

        response = client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get(athlete__id=4)
        self.assertEqual(order.status, "O")

        # Disallowed updates
        for update in (
            {"status": "P"},
            {"status": "O"},
            {"unit_price": "10.0"},
        ):
            response = client.put(self.url + f"{order.pk}/", update, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Order.objects.count(), 1)
            order = Order.objects.get(athlete__id=4)
            self.assertEqual(order.status, "O")
            # self.assertEqual(order.unit_price, Decimal("O.99"))

        # Cancel order
        response = client.put(self.url + f"{order.pk}/", {"status": "C"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get(athlete__id=4)
        self.assertEqual(order.status, "C")

    def test_bank_order(self):

        # Add some past trades to establish athlete value
        athlete = Athlete.objects.get(pk=4)
        entities = Entity.objects.all()
        Trade(
            athlete=athlete,
            buyer=entities[0],
            seller=entities[1],
            unit_price=1.5,
            volume=5.0,
        ).save()

        athlete = Athlete.objects.get(pk=4)
        self.assertEqual(athlete.value, Decimal(1.5))

        # Add some bank shares
        bank = get_cowley_club_bank()
        Share(athlete=athlete, volume=100, owner=get_cowley_club_bank()).save()

        data = {"athlete_id": 4, "volume": "10.0", "unit_price": "1.6", "buy_sell": "B"}

        token = Token.objects.get(user__username="jparkinson")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        response = client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.all()[0]
        self.assertEqual(order.unfilled_volume, Decimal("8.70"))

        trade = Trade.objects.all()
        self.assertEqual(len(trade), 2)
        self.assertEqual(trade[1].unit_price, Decimal("1.60"))

        athlete = Athlete.objects.get(pk=4)
        self.assertEqual(athlete.value, Decimal("1.52"))
