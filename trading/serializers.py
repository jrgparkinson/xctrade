from rest_framework import serializers
from .models import Athlete, Club, Entity, Order, Asset, Share, Trade
from .exceptions import TradingException
import logging

LOGGER = logging.getLogger(__name__)

class ClubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Club
        fields = ('pk', 'name')

class AthleteSerializer(serializers.ModelSerializer):
    club = ClubSerializer(many=False, read_only=True)

    class Meta:
        model = Athlete 
        fields = ('pk', 'name', 'club', 'power_of_10', 'value', "prev_value", "percent_change")
        read_only_fields = ("value", "percent_change", "prev_value")


class EntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entity 
        fields = ('pk', 'name', 'user', 'capital')
        read_only_fields = ('capital', )


class ShareSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(many=False, read_only=True)
    # athlete = serializers.PrimaryKeyRelatedField(queryset=Athlete.objects.all())

    class Meta:
        model = Share 
        fields = ('pk', 'athlete', 'volume')
        # depth = 1

class TradeSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(many=False, read_only=True)
    buyer = EntitySerializer(many=False, read_only=True)
    seller = EntitySerializer(many=False, read_only=True)

    class Meta:
        model = Trade
        # fields = ("pk", "athlete", "volume", "buyer", "seller", "unit_price", "timestamp")
        fields = ("pk", "athlete", "volume", "buyer", "seller", "unit_price", "timestamp")

class TradeSimpleSerializer(serializers.ModelSerializer):
    # athlete = AthleteSerializer(many=False, read_only=True)
    # buyer = EntitySerializer(many=False, read_only=True)
    # seller = EntitySerializer(many=False, read_only=True)

    class Meta:
        model = Trade
        # fields = ("pk", "athlete", "volume", "buyer", "seller", "unit_price", "timestamp")
        fields = ("volume", "unit_price", "timestamp")


class OrderSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(many=False, read_only=True)
    entity = EntitySerializer(many=False, read_only=True)

    athlete_id = serializers.PrimaryKeyRelatedField(queryset=Athlete.objects.all(), write_only=True)

    class Meta:
        model = Order 
        fields = ('pk', 'athlete', 'entity', 'athlete_id', 'volume', 'unit_price', 'buy_sell', 'status')
        read_only_fields = ('status', )

    def create(self, validated_data):
        LOGGER.info("OrderSerializer create: " + str(validated_data))
        
        validated_data["athlete"] = validated_data["athlete_id"]
        validated_data.pop("athlete_id", None)
        user = self.user
        # user = serializers.CurrentUserDefault()
        validated_data["entity"] = user.entity
        # validated_data["entity"] = validated_data["entity_id"]
        # validated_data.pop("entity_id", None)


        return super().create(validated_data)

        # return self.save_with_fields_filled(validated_data)

