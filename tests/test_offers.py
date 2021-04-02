
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trading.athlete import Athlete, Club
from trading.entity import User, Entity
from trading.order import Order
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
        response = self.client.get("/api/athletes/", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), [])


class OrdersTests(APITestCase):

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
                Share(athlete=athlete, volume=10, owner=user.entity).save()


    def test_create_orders(self):
        url = "/api/orders/"
        data = {"athlete_id": 4,
        "volume": "0.99",
        "unit_price": "0.99",
        "buy_sell": "B"}

        token = Token.objects.get(user__username='jparkinson')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        response = client.get(url, format='json')
        self.assertEqual(json.loads(response.content), [{'athlete': {'club': {'name': 'OUCCC', 'pk': 1},
               'name': 'Joseph Woods',
              'pk': 4,
               'power_of_10': ''},
   'buy_sell': 'B',
   'entity': {'capital': '1000.00', 'name': 'jparkinson', 'pk': 1, 'user': 1},
   'pk': 1,
   'status': 'O',
   'unit_price': '0.99',
   'volume': '0.99'}])


        # Now add another order from someone else, check it's actioned
        client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.get(user__username='lcotter').key)

        response = client.post(url, {"athlete_id": 4,
        "volume": "0.2",
        "unit_price": "0.95",
        "buy_sell": "S"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)


        order_buyer = Order.objects.get(entity__user__username='jparkinson')
        order_seller = Order.objects.get(entity__user__username='lcotter')
        self.assertEqual(order_buyer.unfilled_volume, Decimal("0.79"))
        self.assertEqual(order_buyer.status, "O")
        self.assertEqual(order_seller.unfilled_volume, Decimal("0.0"))
        self.assertEqual(order_seller.status, "F")
    
        share_buyer = Share.objects.get(owner__user__username="jparkinson",athlete__name="Joseph Woods")
        share_seller = Share.objects.get(owner__user__username="lcotter",athlete__name="Joseph Woods")
        
        self.assertEqual(share_buyer.volume, Decimal("10.2"))
        self.assertEqual(share_seller.volume, Decimal("9.8"))

        # Price should be 0.2*(0.95+0.99)/2 = 0.194 = 0.19
        buyer = Entity.objects.get(user__username="jparkinson")
        seller = Entity.objects.get(user__username="lcotter")
        self.assertEqual(buyer.capital, Decimal("999.81"))
        self.assertEqual(seller.capital, Decimal("1000.19"))



        # Add another sell trade, check it is also actioned
        response = client.post(url, {"athlete_id": 4,
        "volume": "0.1",
        "unit_price": "0.9",
        "buy_sell": "S"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 3)
        share_buyer = Share.objects.get(owner__user__username="jparkinson",athlete__name="Joseph Woods")
        share_seller = Share.objects.get(owner__user__username="lcotter",athlete__name="Joseph Woods")
        self.assertEqual(share_buyer.volume, Decimal("10.3"))
        self.assertEqual(share_seller.volume, Decimal("9.7"))

        # Price should be 0.1*(0.9+0.99)/2 = 0.09
        buyer = Entity.objects.get(user__username="jparkinson")
        seller = Entity.objects.get(user__username="lcotter")
        self.assertEqual(buyer.capital, Decimal("999.72"))
        self.assertEqual(seller.capital, Decimal("1000.28"))

        # Add a sell trade that's too expensive, shouldn't be actioned
        response = client.post(url, {"athlete_id": 4,
        "volume": "0.1",
        "unit_price": "1.1",
        "buy_sell": "S"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 4)
        order_seller = Order.objects.get(entity__user__username='lcotter',unit_price=Decimal("1.1"))
        self.assertEqual(order_seller.unfilled_volume, Decimal("0.1"))
        self.assertEqual(order_seller.status, "O")

        # Add a sell trade for more shares than owned, shouldn't be created
        response = client.post(url, {"athlete_id": 4,
        "volume": "20",
        "unit_price": "0.6",
        "buy_sell": "S"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 4)

        # Buy trade for more money than we have, shouldn't be created
        response = client.post(url, {"athlete_id": 4,
        "volume": "20",
        "unit_price": "100000",
        "buy_sell": "B"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 4)



    def test_cancel_order(self):
        self.assertEqual(1, 0)
        
  
