import logging
from requests.exceptions import HTTPError
from django.conf import settings
from decimal import Decimal
from django.db.models import Q
from social_django.utils import psa
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework import status
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Athlete, Order, Share, Dividend, Auction, Bid, Loan
from .serializers import *

LOGGER = logging.getLogger(__name__)


class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token.
    """

    access_token = serializers.CharField(allow_blank=False, trim_whitespace=True,)


@api_view(http_method_names=["POST"])
@permission_classes([AllowAny])
@psa()
def exchange_token(request, backend):
    """
    Exchange an OAuth2 access token for one for this site.
    This simply defers the entire OAuth2 process to the front end.
    The front end becomes responsible for handling the entirety of the
    OAuth2 process; we just step in at the end and use the access token
    to populate some user identity.
    The URL at which this view lives must include a backend field, like:
        url(API_ROOT + r'social/(?P<backend>[^/]+)/$', exchange_token),
    Using that example, you could call this endpoint using i.e.
        POST API_ROOT + 'social/facebook/'
        POST API_ROOT + 'social/google-oauth2/'
    Note that those endpoint examples are verbatim according to the
    PSA backends which we configured in settings.py. If you wish to enable
    other social authentication backends, they'll get their own endpoints
    automatically according to PSA.
    ## Request format
    Requests must include the following field
    - `access_token`: The OAuth2 access token provided by the provider
    """
    serializer = SocialSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        # set up non-field errors key
        # http://www.django-rest-framework.org/api-guide/exceptions/#exception-handling-in-rest-framework-views
        try:
            nfe = settings.NON_FIELD_ERRORS_KEY
        except AttributeError:
            nfe = "non_field_errors"

        try:
            # this line, plus the psa decorator above, are all that's necessary to
            # get and populate a user object for any properly enabled/configured backend
            # which python-social-auth can handle.
            user = request.backend.do_auth(serializer.validated_data["access_token"])
        except HTTPError as e:
            # An HTTPError bubbled up from the request to the social auth provider.
            # This happens, at least in Google's case, every time you send a malformed
            # or incorrect access key.
            return Response(
                {"errors": {"token": "Invalid token", "detail": str(e),}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user:
            if user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key})
            else:
                # user is not active; at some point they deleted their account,
                # or were banned by a superuser. They can't just log in with their
                # normal credentials anymore, so they can't log in with social
                # credentials either.
                return Response(
                    {"errors": {nfe: "This user account is inactive"}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Unfortunately, PSA swallows any information the backend provider
            # generated as to why specifically the authentication failed;
            # this makes it tough to debug except by examining the server logs.
            return Response(
                {"errors": {nfe: "Authentication Failed"}},
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])
def athletes_list(request):
    # LOGGER.info("User: %s" % user)
    if request.method == "GET":
        data = Athlete.objects.all()
        serializer = AthleteSerializer(data, context={"request": request}, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def entities_list(request):
    if request.method == "GET":
        data = Entity.objects.all().filter(is_bank=False)
        serializer = EntitySerializer(data, context={"request": request}, many=True)
        return Response(serializer.data)


@api_view(["GET", "PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    if request.method == "GET":
        data = user.entity
        serializer = EntitySerializer(data, context={"request": request}, many=False)
        return Response(serializer.data)
    elif request.method == "PUT":
        if "name" in request.data:
            user.entity.name = request.data["name"]
        else:
            return Response(
                "Only profile update allowed is name change",
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.entity.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def auction_shares(request):
    auction = Auction.get_active_auction()

    if not auction:
        return Response("No current auction found", status=status.HTTP_404_NOT_FOUND)

    serializer = ShareSerializer(
        auction.available_shares(), context={"request": request}, many=True
    )
    return Response(serializer.data)


@api_view(["GET"])
def active_auction(request):
    auction = Auction.get_active_auction()

    if not auction:
        return Response("No current auction found", status=status.HTTP_404_NOT_FOUND)

    serializer = AuctionSerializer(auction, context={"request": request}, many=False)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def bids_list(request, auction_pk):
    if request.method == "GET":
        bids = Bid.objects.all().filter(
            auction__pk=auction_pk, bidder=request.user.entity
        )
        # LOGGER.info("Bids: %s" % bids)
        serializer = BidSerializer(bids, context={"request": request}, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        # Save the bids
        LOGGER.info(request.data)
        serializer = BidSerializer(data=request.data, many=True, user=request.user)
        # serializer.user = request.user
        LOGGER.info("Valid serializer? %s " % serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def shares_list(request):
    user = request.user
    data = Share.objects.all().filter(owner=user.entity)
    serializer = ShareSerializer(data, context={"request": request}, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def trades_list(request):
    if request.method == "GET":
        data = Trade.objects.all().order_by("timestamp")

        Serializer = TradeSerializer

        if "athlete_id" in request.query_params:
            data = data.filter(athlete__id=request.query_params["athlete_id"])
            Serializer = TradeSimpleSerializer

        if "entity_id" in request.query_params:
            data = data.filter(
                Q(buyer__id=request.query_params["entity_id"])
                | Q(seller__id=request.query_params["entity_id"])
            )

        serializer = Serializer(data, context={"request": request}, many=True)
        return Response(serializer.data)


@api_view(["GET", "POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def orders_list(request):
    """
    post example:
    {"athlete_id": 7,
        "volume": "0.99",
        "unit_price": "0.99",
        "buy_sell": "B"}
"""
    if request.method == "GET":
        user = request.user
        data = []
        if user.is_authenticated:
            data = Order.objects.all().filter(
                entity=user.entity
            )  # , status=Order.OPEN)

            if "athlete_id" in request.query_params:
                data = data.filter(athlete__id=request.query_params["athlete_id"])

            if "entity_id" in request.query_params:
                data = data.filter(entity__id=request.query_params["entity_id"])

        serializer = OrderSerializer(data, context={"request": request}, many=True)

        return Response(serializer.data)

    elif request.method == "POST":
        serializer = OrderSerializer(data=request.data)
        serializer.user = request.user
        # LOGGER.info("User: %s", request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def athlete_detail(request, pk):
    try:
        obj = Athlete.objects.get(pk=pk)
    except Athlete.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = AthleteSerializer(obj, context={"request": request}, many=False)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def order_prices(request, athlete_pk):
    user = request.user
    athlete = Athlete.objects.get(pk=athlete_pk)
    entity = user.entity  # type: Entity

    # Retrieve:
    # available capital, shares in athlete owned, current athlete price
    data = {
        "capital": entity.capital,
        "shares_owned": entity.vol_owned(athlete),
    }
    return Response(data)


@api_view(["PUT"])
def orders_detail(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # the only update allowed by the user is to cancel the order
    if "status" in request.data and request.data["status"] == "C":
        order.status = request.data["status"]
        order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(
        "Only order update allowed is cancelling", status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
def races_list(request):
    data = Race.objects.all()
    serializer = RaceSerializer(data, context={"request": request}, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def results_list(request):
    athlete_pk = request.query_params["athlete_id"]
    data = Result.objects.all().filter(athlete__pk=athlete_pk)
    serializer = ResultSerializer(data, context={"request": request}, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def dividends_list(request):
    user = request.user
    data = Dividend.objects.all().filter(entity=user.entity, reverted=False)
    serializer = DividendSerializer(data, context={"request": request}, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def races_detail(request, pk):
    race = Race.objects.get(pk=pk)
    serializer = RaceDetailSerializer(race, context={"request": request}, many=False)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def loans_list(request):
    if request.method == "GET":
        data = Loan.objects.all().filter(recipient=request.user.entity)
        serializer = LoanSerializer(data, context={"request": request}, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        LOGGER.info(request.data)
        serializer = LoanSerializer(data=request.data, many=True, user=request.user)
        LOGGER.info("Valid serializer? %s " % serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def loan_detail(request, pk):
    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # the only update allowed by the user is to reduce the capital i.e. make a repayment
    if "balance" in request.data:
        repay_ammount = loan.balance - Decimal(request.data["balance"])
        loan.repay_loan(repay_ammount)
        loan.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(
        "Only loan update allowed is repayment", status=status.HTTP_400_BAD_REQUEST
    )