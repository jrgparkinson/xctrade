import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from trading.loan import apply_all_interest

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """ Compute interest for loans """

    help = "Compute interest for loans"

    def handle(self, *args, **kwargs):
        apply_all_interest()
        LOGGER.info("Finished computing interest")
