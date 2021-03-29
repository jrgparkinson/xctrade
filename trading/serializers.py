from rest_framework import serializers
from .models import Athlete, Club, Entity, Offer, Asset, Share
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
        fields = ('pk', 'name', 'club', 'power_of_10')


class ShareSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(many=False, read_only=True)
    # athlete = serializers.PrimaryKeyRelatedField(queryset=Athlete.objects.all())

    class Meta:
        model = Share 
        fields = ('pk', 'athlete', 'volume')
        # depth = 1


# class AssetGenericSerializer(serializers.Serializer):
#     """ Serializer that renders each instance with its own specific serializer """

#     def to_representation(self, instance):
#         if isinstance(instance, Share):
#             return ShareSerializer(instance=instance).data
#         # elif instance.is_future():
#         #     return FutureSerializer(instance=instance.contract.future).data
#         # elif instance.is_option():
#         #     return OptionSerializer(instance=instance.contract.future.option).data
#         # else:
#         #     return AssetSerializer(instance=instance).data


#     def to_internal_value(self, data):
#         if "type" not in data or data["type"].lower() == "share":
#             return ShareSerializer().to_internal_value(data)
#         # elif data["type"].lower() == "future":
#         #     return FutureSerializer().to_internal_value(data)
#         # elif data["type"].lower() == "option":
#         #     return OptionSerializer().to_internal_value(data)
#         else:
#             raise TradingException("Unknown asset type {}".format(data["type"]))

#     def get_serializer(data):
#         # if "type" not in data.keys() or data["type"].lower() == "share" or "athlete" in data.keys():
#         #     if isinstance(data["athlete"], Athlete):
#         #         data["athlete"] = data["athlete"].id
#         return ShareSerializer(data=data)
#         # elif "buyer" in data.keys() and "option_holder" in data.keys():
#         #     return OptionSerializer(data=data) 
#         # elif "buyer" in data.keys():
#         #     return FutureSerializer(data=data)
#         # else:
#         #     raise TradingException("Unknown asset type: {}".format(data))
        


class OfferSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(many=False, read_only=True)
    athlete_id = serializers.PrimaryKeyRelatedField(queryset=Athlete.objects.all(), write_only=True)

    class Meta:
        model = Offer 
        fields = ('pk', 'athlete', 'athlete_id', 'volume', 'unit_price', 'buy_sell', 'status')
        read_only_fields = ('status', )

    def create(self, validated_data):
        LOGGER.info("OfferSerializer create: " + str(validated_data))
        
        # Get athlete
        # athlete = Athlete.objects.get(pk=self.data["athlete_id"])
        # asset_serializer = AssetGenericSerializer.get_serializer(validated_data["asset"])
        # if (asset_serializer.is_valid() == False):
        #     LOGGER.info(asset_serializer.errors)
        #     return None
        # asset = asset_serializer.save()
        # # asset.save()


        validated_data["athlete"] = validated_data["athlete_id"]
        validated_data.pop("athlete_id", None)

        # TODO: Fill with logged in user
        validated_data["entity"] = Entity.objects.get(pk=1)

        return super().create(validated_data)

        # return self.save_with_fields_filled(validated_data)


class EntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entity 
        fields = ('pk', 'name', 'capital')
        read_only_fields = ('capital', )