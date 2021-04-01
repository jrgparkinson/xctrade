
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trading.athlete import Athlete, Club
from trading.entity import User
from trading.order import Order
import json
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

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


        # Now add another order from someone else
        client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.get(user__username='lcotter').key)

        response = client.post(url, {"athlete_id": 4,
        "volume": "0.2",
        "unit_price": "0.95",
        "buy_sell": "S"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)

        # Check they've been matched/executed
        

   
