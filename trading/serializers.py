import logging
from rest_framework import serializers
from .models import (
    Athlete,
    Club,
    Entity,
    Order,
    Share,
    Trade,
    Race,
    Result,
    Dividend,
    Auction,
    Bid,
    Loan,
    LoanPolicy
)
from .entity import get_cowley_club_bank

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
        fields = ("pk", "name", "user", "capital", "portfolio_value", "total_debt")
        read_only_fields = ("capital", "portfolio_value", "user", "total_debt")


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
        read_only_fields = ("status", "unfilled_volume", "athlete", "entity")

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data["athlete"] = validated_data["athlete_id"]
        validated_data.pop("athlete_id", None)
        user = self.user
        validated_data["entity"] = user.entity
        return super().create(validated_data)


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


class AuctionSerializer(serializers.ModelSerializer):
    bank = EntitySerializer(many=False, read_only=True)

    class Meta:
        model = Auction
        fields = (
            "pk",
            "name",
            "description",
            "start_date",
            "end_date",
            "bank",
        )


class BidSerializer(serializers.ModelSerializer):
    bidder = EntitySerializer(many=False, read_only=True)
    athlete = serializers.PrimaryKeyRelatedField(queryset=Athlete.objects.all())
    auction = serializers.PrimaryKeyRelatedField(queryset=Auction.objects.all())

    class Meta:
        model = Bid
        fields = (
            "pk",
            "status",
            "bidder",
            "auction",
            "athlete",
            "volume",
            "price_per_volume",
        )

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        user = self.user
        validated_data["bidder"] = user.entity

        LOGGER.info(validated_data)

        # Delete existing object
        Bid.objects.all().filter(
            athlete=validated_data["athlete"], bidder=validated_data["bidder"]
        ).delete()

        return super().create(validated_data)

class LoanInfoSerializer(serializers.ModelSerializer):
    """ Serializer Loan objects """

    lender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LoanPolicy
        fields = (
            "pk",
            "lender",
            "max_balance",
            "interest_interval",
            "interest_rate",
        )

    def to_representation(self, instance):
        """ Encode time interval as number of days """
        data = super(LoanInfoSerializer, self).to_representation(instance)
        data["interest_interval"] = instance.interest_interval.days
        return data

    # def create(self, validated_data):
    #     # user = self.user
    #     # validated_data["recipient"] = user.entity
    #     validated_data["lender"] = get_cowley_club_bank()

    #     LOGGER.info(validated_data)

    #     return super().create(validated_data)



class LoanSerializer(serializers.ModelSerializer):
    """ Serializer Loan objects """

    loan_info = LoanInfoSerializer(many=False, read_only=True)
    loan_info_id = serializers.PrimaryKeyRelatedField(queryset=LoanPolicy.objects.all(), write_only=True)

    class Meta:
        model = Loan
        fields = (
            "pk",
            "loan_info",
            "loan_info_id",
            "created",
            "balance",
            "interest_last_added",
        )

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        user = self.user
        validated_data["recipient"] = user.entity
        validated_data["loan_info"] = validated_data["loan_info_id"]
        validated_data.pop("loan_info_id", None)
        # validated_data["lender"] = get_cowley_club_bank()

        LOGGER.info(validated_data)

        return super().create(validated_data)


