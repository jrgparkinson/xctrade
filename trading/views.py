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
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Athlete,
    Order,
    Share,
    Dividend,
    Auction,
    Bid,
    Loan,
    Trade,
    Race,
    Result,
    Entity,
)
from .serializers import (
    EntitySerializer,
    TradeSimpleSerializer,
    RaceSerializer,
    ResultSerializer,
    RaceDetailSerializer,
    AthleteSerializer,
    OrderSerializer,
    ShareSerializer,
    DividendSerializer,
    AuctionSerializer,
    BidSerializer,
    LoanSerializer,
)


LOGGER = logging.getLogger(__name__)


athlete_id_param = openapi.Parameter(
    "athlete_id", openapi.IN_QUERY, description="Athlete ID", type=openapi.TYPE_INTEGER
)
auction_id_param = openapi.Parameter(
    "auction_id", openapi.IN_QUERY, description="Auction ID", type=openapi.TYPE_INTEGER
)

create_order_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["athlete_id", "volume", "unit_price", "buy_sell"],
    properties={
        "athlete_id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "volume": openapi.Schema(type=openapi.TYPE_NUMBER),
        "unit_price": openapi.Schema(type=openapi.TYPE_NUMBER),
        "buy_sell": openapi.Schema(type=openapi.TYPE_STRING, enum=("B", "S")),
    },
)

order_update_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["status"],
    properties={"status": openapi.Schema(type=openapi.TYPE_STRING, enum=("C",)),},
)

profile_update_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["name"],
    properties={"name": openapi.Schema(type=openapi.TYPE_STRING),},
)


loan_create = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["balance", "interest_rate"],
    properties={
        "balance": openapi.Schema(type=openapi.TYPE_NUMBER),
        "loan_info_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Loan info ID"),
    },
)
loan_update = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["balance"],
    properties={
        "balance": openapi.Schema(
            type=openapi.TYPE_NUMBER,
            description="New balance after repaying some ammount",
        ),
    },
)
bid_create = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["auction", "athlete", "volume", "price_per_volume",],
    properties={
        "auction": openapi.Schema(type=openapi.TYPE_INTEGER, description="Auction ID"),
        "athlete": openapi.Schema(type=openapi.TYPE_INTEGER, description="Athlete ID"),
        "volume": openapi.Schema(type=openapi.TYPE_NUMBER),
        "price_per_volume": openapi.Schema(type=openapi.TYPE_NUMBER),
    },
)


class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token.
    """

    access_token = serializers.CharField(allow_blank=False, trim_whitespace=True,)


@swagger_auto_schema(method="POST", permission_classes=(IsAdminUser,))
@api_view(http_method_names=["POST"])
@permission_classes([AllowAny])
@psa()
def exchange_token(request, backend):  # pylint: disable=W0613
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


@swagger_auto_schema(method="get", responses={200: AthleteSerializer})
@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])
def athletes_list(request):
    """ Get a list of all athletes """
    if request.method == "GET":
        data = Athlete.objects.all()
        serializer = AthleteSerializer(data, context={"request": request}, many=True)
        return Response(serializer.data)


@swagger_auto_schema(method="get", responses={200: EntitySerializer})
@api_view(["GET"])
def entities_list(request):
    """ Get a list of all entities (players) """
    if request.method == "GET":
        data = Entity.objects.all().filter(is_bank=False)
        serializer = EntitySerializer(data, context={"request": request}, many=True)
        return Response(serializer.data)


@swagger_auto_schema(
    method="get", responses={200: EntitySerializer}, security=[{"Token": []}]
)
@swagger_auto_schema(
    operation_description="Update profile",
    method="PUT",
    request_body=profile_update_request,
    security=[{"Token": []}],
)
@api_view(["GET", "PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    """ Retrieve or update your user profile """
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


@swagger_auto_schema(method="get", responses={200: ShareSerializer})
@api_view(["GET"])
def auction_shares(request):
    """ Shares available to bid on at an auction """
    auction = Auction.get_active_auction()

    if not auction:
        return Response("No current auction found", status=status.HTTP_404_NOT_FOUND)

    serializer = ShareSerializer(
        auction.available_shares(), context={"request": request}, many=True
    )
    return Response(serializer.data)


@swagger_auto_schema(method="get", responses={200: AuctionSerializer})
@api_view(["GET"])
def active_auction(request):
    """ Retrieve the current auction (if any) """
    auction = Auction.get_active_auction()

    if not auction:
        return Response("No current auction found", status=status.HTTP_404_NOT_FOUND)

    serializer = AuctionSerializer(auction, context={"request": request}, many=False)
    return Response(serializer.data)


@swagger_auto_schema(
    operation_description="Create bid",
    method="POST",
    request_body=bid_create,
    security=[{"Token": []}],
)
@swagger_auto_schema(
    method="get", responses={200: BidSerializer}, security=[{"Token": []}]
)
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def bids_list(request, auction_pk):
    """ Get or create bids for the authenticated user and given auction """
    if request.method == "GET":
        bids = Bid.objects.all().filter(
            auction__pk=auction_pk, bidder=request.user.entity
        )
        serializer = BidSerializer(bids, context={"request": request}, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        # Save the bids
        LOGGER.info(request.data)
        serializer = BidSerializer(data=request.data, many=True, user=request.user)
        LOGGER.info("Valid serializer? %s " % serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get", responses={200: ShareSerializer}, security=[{"Token": []}]
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def shares_list(request):
    """ Get shares owner by authenticated user """
    user = request.user
    data = Share.objects.all().filter(owner=user.entity)
    serializer = ShareSerializer(data, context={"request": request}, many=True)
    return Response(serializer.data)


# Need to rethink this end point
@swagger_auto_schema(
    method="get",
    manual_parameters=[athlete_id_param],
    responses={200: TradeSimpleSerializer},
)
@api_view(["GET"])
def trades_list(request):
    """ Get trades for an athlete """
    if request.method == "GET":
        data = Trade.objects.all().order_by("timestamp")

        # Serializer = TradeSerializer

        if "athlete_id" in request.query_params:
            data = data.filter(athlete__id=request.query_params["athlete_id"])

        # if "entity_id" in request.query_params:
        #     data = data.filter(
        #         Q(buyer__id=request.query_params["entity_id"])
        #         | Q(seller__id=request.query_params["entity_id"])
        #     )

        serializer = TradeSimpleSerializer(
            data, context={"request": request}, many=True
        )
        return Response(serializer.data)


@swagger_auto_schema(
    operation_description="Get list of orders",
    method="get",
    manual_parameters=[athlete_id_param],
    responses={200: OrderSerializer},
)
@swagger_auto_schema(
    operation_description="Create new order",
    method="post",
    request_body=create_order_request,
    security=[{"Token": []}],
)
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def orders_list(request):
    """ Handle orders """
    if request.method == "GET":
        user = request.user
        data = []
        if user.is_authenticated:
            data = Order.objects.all().filter(entity=user.entity)

            if "athlete_id" in request.query_params:
                data = data.filter(athlete__id=request.query_params["athlete_id"])

            # if "entity_id" in request.query_params:
            #     data = data.filter(entity__id=request.query_params["entity_id"])

        serializer = OrderSerializer(data, context={"request": request}, many=True)

        return Response(serializer.data)

    elif request.method == "POST":
        serializer = OrderSerializer(data=request.data)
        serializer.user = request.user
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="get", responses={200: AthleteSerializer})
@api_view(["GET"])
def athlete_detail(request, pk):
    """ Get detailed information about an athlete """
    try:
        obj = Athlete.objects.get(pk=pk)
    except Athlete.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = AthleteSerializer(obj, context={"request": request}, many=False)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    security=[{"Token": []}],
    responses={
        200: openapi.Response(
            description="Cash and shares for user",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                # required=["name"],
                properties={
                    "capital": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "shares_owned": openapi.Schema(type=openapi.TYPE_NUMBER),
                },
            ),
        )
    },
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def order_prices(request, athlete_pk):
    """ Retrieve available cash and shares in an athlete """
    user = request.user
    athlete = Athlete.objects.get(pk=athlete_pk)
    entity = user.entity  # type: Entity

    # Retrieve:
    data = {
        "capital": entity.capital,
        "shares_owned": entity.vol_owned(athlete),
    }
    return Response(data)


@swagger_auto_schema(
    operation_description="Update order",
    method="PUT",
    request_body=order_update_request,
    security=[{"Token": []}],
)
@api_view(["PUT"])
def orders_detail(request, pk):
    """ Update an order - only allowed operation is to cancel it """
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


@swagger_auto_schema(method="get", responses={200: RaceSerializer})
@api_view(["GET"])
def races_list(request):
    """ Retrieve races """
    data = Race.objects.all()
    serializer = RaceSerializer(data, context={"request": request}, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    responses={200: ResultSerializer},
    manual_parameters=[athlete_id_param],
)
@api_view(["GET"])
def results_list(request):
    """ Retrieve results """
    if "athlete_id" in request.query_params:
        athlete_pk = request.query_params["athlete_id"]
        data = Result.objects.all().filter(athlete__pk=athlete_pk)
    else:
        data = Result.objects.all()
    serializer = ResultSerializer(data, context={"request": request}, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get", responses={200: DividendSerializer}, security=[{"Token": []}]
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def dividends_list(request):
    """ Retrieve dividends for the authenticated user """
    user = request.user
    data = Dividend.objects.all().filter(entity=user.entity, reverted=False)
    serializer = DividendSerializer(data, context={"request": request}, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method="get", responses={200: RaceDetailSerializer})
@api_view(["GET"])
def races_detail(request, pk):
    """ Get detailed information about a race """
    race = Race.objects.get(pk=pk)
    serializer = RaceDetailSerializer(race, context={"request": request}, many=False)
    return Response(serializer.data)


@swagger_auto_schema(
    operation_description="Create loan",
    method="POST",
    request_body=loan_create,
    security=[{"Token": []}],
)
@swagger_auto_schema(
    method="get", responses={200: LoanSerializer}, security=[{"Token": []}]
)
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def loans_list(request):
    """ Get/create loans for the authenticated user """
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


@swagger_auto_schema(
    operation_description="Update loan",
    method="PUT",
    request_body=loan_update,
    security=[{"Token": []}],
)
@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def loan_detail(request, pk):
    """ Update a loan """
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
