from .athlete import Athlete, Club
from .order import Order, Trade
from .entity import User, Entity, get_cowley_club_bank
from .asset import Asset, Share
from .races import Race, Result, Dividend
from .auction import Auction, Bid
from .loan import Loan
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Q
import logging
from decimal import Decimal

LOGGER = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        entity = Entity.objects.create(user=instance)
        entity.save()


@receiver(post_save, sender=Dividend)
def pay_dividend(sender, instance, created, **kwargs):
    """ Pay dividend object after creating it """
    if created:
        instance.pay()
        instance.save()


# @receiver(post_save, sender=Trade)
# def execute_trade(sender, instance, created, **kwargs):
#     """ Pay execute trade upon creation """
#     if created:
#         instance.do_trade()
#         instance.save()

@receiver(pre_save, sender=Trade)
def execute_trade(sender, instance, **kwargs):
    """ Pay execute trade upon creation """
    if instance.pk is None:
        instance.do_trade()
        # instance.save()
    # else:
    #     instance.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # LOGGER.info("Save user with entity name: %s" % instance.entity.name)
    if instance.entity.name == "" and (
        instance.first_name != "" or instance.last_name != ""
    ):
        instance.entity.name = f"{instance.first_name} {instance.last_name}"
        # LOGGER.info("Set name = %s" % instance.entity.name)
    instance.entity.save()


@receiver(post_save, sender=Order)
def match_order(sender, instance, created, **kwargs):
    """ Find matching orders """
    if created:

        matching_orders = Order.objects.all().filter(
            Q(athlete=instance.athlete)
            & Q(buy_sell=instance.opposite_buy_sell())
            & Q(status=Order.OPEN)
            & ~Q(entity=instance.entity)
        )
        if instance.is_buy():
            matching_orders = matching_orders.filter(
                unit_price__lte=instance.unit_price
            ).order_by("unit_price")
        else:
            matching_orders = matching_orders.filter(
                unit_price__gte=instance.unit_price
            ).order_by("-unit_price")

        # LOGGER.info("Matching orders: %s" % matching_orders)

        vol_unfilled = instance.volume
        order_vols = []

        for matched_order in matching_orders:
            vol_from_order = min(vol_unfilled, matched_order.unfilled_volume)

            # Check other party can fulfil order, assuming already we can fulfill
            if not matched_order.can_fulfil(vol_from_order):
                continue

            order_vols.append((matched_order, vol_from_order))
            vol_unfilled -= vol_from_order

            if vol_unfilled == 0.0:
                break

        # LOGGER.info("Orders to use: %s", order_vols)
        # We can fill part of this order
        # if vol_unfilled > 0.0:
        #     return

        # By now, we can start filling orders
        for order_vol in order_vols:
            LOGGER.info("Fill with %s", (order_vol))
            other_order = order_vol[0]
            vol = order_vol[1]
            instance.fill_with(other_order, vol)

            other_order.save()
            instance.save()

        # If remaining unfilled, see if bank can fill it
        if instance.unfilled_volume <= Decimal(0):
            return

        bank = get_cowley_club_bank()
        if not bank:
            return

        bank_fill_vol = instance.unfilled_volume

        bank_can_fill = False

        while not bank_can_fill and bank_fill_vol > Decimal(0):
            # if we're selling, get the bank offer to buy
            bank_offer = bank.get_bank_offer(
                instance.athlete, bank_fill_vol, instance.opposite_buy_sell_long
            )
            bank_can_fill = bank_offer is not None and (
                (instance.is_buy() and bank_offer <= instance.unit_price)
                or (instance.is_sell() and bank_offer >= instance.unit_price)
            )

            if not bank_can_fill:
                bank_fill_vol -= Decimal(0.1)

        if bank_can_fill and bank_fill_vol > Decimal(0):
            # Do the trade for this volume
            buyer = instance.entity if instance.is_buy() else bank
            seller = instance.entity if instance.is_sell() else bank
            Trade(
                athlete=instance.athlete,
                volume=bank_fill_vol,
                buyer=buyer,
                seller=seller,
                unit_price=bank_offer,
            ).save()

            instance.unfilled_volume -= bank_fill_vol
            instance.save()
