from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Athlete, Offer
from .serializers import *

@api_view(['GET']) # , 'POST'])
def athletes_list(request):
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

@api_view(['GET', 'POST'])
def offers_list(request):
    """
    post example:
    {"athlete_id": 7,
        "volume": "0.99",
        "unit_price": "0.99",
        "buy_sell": "B"}
"""
    if request.method == 'GET':
        data = Offer.objects.all()

        serializer = OfferSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OfferSerializer(data=request.data)
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