from .athlete import Athlete, Club
from .order import Order
from .entity import User, Entity
from .asset import Asset, Share
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Q
import logging

LOGGER = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Entity.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.entity.save()


# @receiver(pre_save, sender=Order)
# def check_valid_order(sender, instance, **kwargs):
#     if not instance.can_fulfil(instance.volume):
#         raise Exception("Insufficient shares or funds to create order")

@receiver(post_save, sender=Order)
def match_order(sender, instance, created, **kwargs):
    """ Find matching orders """
    if created:
        
        matching_orders = Order.objects.all().filter(Q(athlete=instance.athlete) & 
                                                     Q(buy_sell=instance.opposite_buy_sell()) &
                                                     Q(status=Order.OPEN) &
                                                     ~Q(entity=instance.entity))
        if instance.is_buy():
            matching_orders = matching_orders.filter(unit_price__lte=instance.unit_price).order_by('unit_price')
        else:
            matching_orders = matching_orders.filter(unit_price__gte=instance.unit_price).order_by('-unit_price')

        LOGGER.info("Matching orders: %s" % matching_orders)

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

        if vol_unfilled > 0.0:
            return

        # By now, we can start filling orders

        # Check we can fulfill
        # if instance.is_buy():

        for order_vol in order_vols:
            other_order = order_vol[0]
            vol = order_vol[1]
            instance.fill_with(other_order, vol)

            other_order.save()
            instance.save()
            



