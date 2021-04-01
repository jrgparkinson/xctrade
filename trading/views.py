from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status

from .models import Athlete, Order
from .serializers import *

from django.conf import settings
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from requests.exceptions import HTTPError
from social_django.utils import psa

import logging

LOGGER = logging.getLogger(__name__)

class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token.
    """
    access_token = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )


@api_view(http_method_names=['POST'])
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
            nfe = 'non_field_errors'

        try:
            # this line, plus the psa decorator above, are all that's necessary to
            # get and populate a user object for any properly enabled/configured backend
            # which python-social-auth can handle.
            user = request.backend.do_auth(serializer.validated_data['access_token'])
        except HTTPError as e:
            # An HTTPError bubbled up from the request to the social auth provider.
            # This happens, at least in Google's case, every time you send a malformed
            # or incorrect access key.
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user:
            if user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
            else:
                # user is not active; at some point they deleted their account,
                # or were banned by a superuser. They can't just log in with their
                # normal credentials anymore, so they can't log in with social
                # credentials either.
                return Response(
                    {'errors': {nfe: 'This user account is inactive'}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Unfortunately, PSA swallows any information the backend provider
            # generated as to why specifically the authentication failed;
            # this makes it tough to debug except by examining the server logs.
            return Response(
                {'errors': {nfe: "Authentication Failed"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

@api_view(['GET'])
def athletes_list(request):
    user = request.user
    LOGGER.info("User: %s" % user)
    if request.method == 'GET':
        data = Athlete.objects.all()

        serializer = AthleteSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AthleteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def entities_list(request):
    if request.method == 'GET':
        data = Entity.objects.all()
        serializer = EntitySerializer(data, context={'request': request}, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
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
    if request.method == 'GET':
        data = Order.objects.all()

        serializer = OrderSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)
        serializer.user = request.user
        LOGGER.info("User: %s", request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['PUT', 'DELETE'])
# def athletes_detail(request, pk):
#     try:
#         Athlete = Athlete.objects.get(pk=pk)
#     except Athlete.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'PUT':
#         serializer = athleteserializer(Athlete, data=request.data,context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':
#         Athlete.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)