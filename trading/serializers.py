from rest_framework import serializers
from .models import Athlete, Club, Entity, Order, Asset, Share, Trade, Race, Result, Dividend
from .exceptions import TradingException
import logging

LOGGER = logging.getLogger(__name__)


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ("pk", "name")


class AthleteShortSerializer(serializers.ModelSerializer):
    club = ClubSerializer(many=False, read_only=True)

    class Meta:
        model = Athlete
        fields = ("pk", "name", "club")


class AthleteSerializer(serializers.ModelSerializer):
    club = ClubSerializer(many=False, read_only=True)

    class Meta:
        model = Athlete
        fields = (
            "pk",
            "name",
            "club",
            "power_of_10",
            "value",
            "prev_value",
            "percent_change",
            "weekly_volume",
        )
        read_only_fields = ("value", "percent_change", "prev_value", "weekly_volume")


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ("pk", "name", "user", "capital", "portfolio_value")
        read_only_fields = ("capital", "portfolio_value", "user")


class ShareSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(many=False, read_only=True)
    # athlete = serializers.PrimaryKeyRelatedField(queryset=Athlete.objects.all())

    class Meta:
        model = Share
        fields = ("pk", "athlete", "volume")
        # depth = 1


class TradeSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(many=False, read_only=True)
    buyer = EntitySerializer(many=False, read_only=True)
    seller = EntitySerializer(many=False, read_only=True)

    class Meta:
        model = Trade
        # fields = ("pk", "athlete", "volume", "buyer", "seller", "unit_price", "timestamp")
        fields = (
            "pk",
            "athlete",
            "volume",
            "buyer",
            "seller",
            "unit_price",
            "timestamp",
        )


class TradeSimpleSerializer(serializers.ModelSerializer):
    # athlete = AthleteSerializer(many=False, read_only=True)
    # buyer = EntitySerializer(many=False, read_only=True)
    # seller = EntitySerializer(many=False, read_only=True)
    unit_price = serializers.FloatField()

    class Meta:
        model = Trade
        # fields = ("pk", "athlete", "volume", "buyer", "seller", "unit_price", "timestamp")
        fields = ("volume", "unit_price", "timestamp")


class OrderSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(many=False, read_only=True)
    entity = EntitySerializer(many=False, read_only=True)

    athlete_id = serializers.PrimaryKeyRelatedField(
        queryset=Athlete.objects.all(), write_only=True
    )

    class Meta:
        model = Order
        fields = (
            "pk",
            "athlete",
            "entity",
            "athlete_id",
            "volume",
            "unfilled_volume",
            "unit_price",
            "buy_sell",
            "status",
        )
        read_only_fields = ("status", "unfilled_volume")

    def create(self, validated_data):
        # LOGGER.info("OrderSerializer create: " + str(validated_data))

        validated_data["athlete"] = validated_data["athlete_id"]
        validated_data.pop("athlete_id", None)
        user = self.user
        # user = serializers.CurrentUserDefault()
        validated_data["entity"] = user.entity
        # validated_data["entity"] = validated_data["entity_id"]
        # validated_data.pop("entity_id", None)

        return super().create(validated_data)

        # return self.save_with_fields_filled(validated_data)


class RaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Race
        fields = (
            "pk",
            "name",
            "time",
            "results_link",
            "event_details_link",
            "max_dividend",
            "min_dividend",
            "num_competitors",
            "has_results",
        )


class ResultSerializer(serializers.ModelSerializer):
    race = RaceSerializer(many=False, read_only=True)
    athlete = AthleteSerializer(many=False, read_only=True)

    class Meta:
        model = Result
        fields = (
            "pk",
            "athlete",
            "race",
            "position",
            "time",
            "dividend",
            "dividend_distributed",
        )
        # read_only_fields = ('capital', )


class ResultForRaceSerializer(serializers.ModelSerializer):
    athlete = AthleteShortSerializer(many=False, read_only=True)

    class Meta:
        model = Result
        fields = (
            "pk",
            "athlete",
            "position",
            "time",
            "dividend",
            "dividend_distributed",
        )


class RaceDetailSerializer(serializers.ModelSerializer):

    results = ResultForRaceSerializer(source="result_set", many=True)

    class Meta:
        model = Race
        fields = (
            "pk",
            "name",
            "time",
            "results_link",
            "event_details_link",
            "max_dividend",
            "min_dividend",
            "num_competitors",
            "results",
            "has_results",
        )

class DividendSerializer(serializers.ModelSerializer):
    result = ResultSerializer(many=False, read_only=True)
    entity = EntitySerializer(many=False, read_only=True)

    class Meta:
        model = Dividend
        fields = (
            "pk",
            "result",
            "entity",
            "volume",
            "dividend_per_share",
            "reverted",
        )
