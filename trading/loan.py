""" Loans """
import logging
import pytz
from datetime import datetime, timedelta
from django.db.models.signals import pre_save
from django.db import models
from django.dispatch import receiver
from .entity import Entity

LOGGER = logging.getLogger(__name__)

class Loan(models.Model):
    """
    One entity may loan another entity some capital, which is repayed at some interest rate
    """

    lender = models.ForeignKey(
        Entity,
        related_name="%(app_label)s_%(class)s_lender",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    recipient = models.ForeignKey(
        Entity,
        related_name="%(app_label)s_%(class)s_recipient",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    created = models.DateTimeField(auto_now_add=True)
    interest_last_added = models.DateTimeField(null=True)

    # Interest rate as a fraction e.g. 0.01 = 1% on the repayment interval
    interest_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Fractional interest rate")
    interest_interval = models.DurationField(default=timedelta(days=7))

    # How much needs to be repayed
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return "Loan of {} from {} to {} ({}% interest)".format(
            self.balance, self.lender, self.recipient, self.interest_rate
        )

    def create_loan(self):
        # Perform checks
        # Can't lend money you don't have
        # if self.lender.capital < self.balance:
        #     raise InsufficienFundsException(
        #         "Lender has {} which is less than the balance {}".format(
        #             self.lender.capital, self.balance
        #         )
        #     )

        # Will throw an exception if not possible
        self.lender.transfer_cash_to(self.recipient, self.balance)
        self.lender.save()
        self.recipient.save()
       
        # Loan.schedule_accrue_interest(loan.id, repeat=interval.total_seconds(), repeat_until=None)    

    
    # @background(schedule=0)
    # def schedule_accrue_interest(loan_id):
    #     loan = Loan.objects.get(id=loan_id)
    #     loan.accrue_interest()


    def accrue_interest(self):

        if self.balance == 0:
            return
            # raise Exception("Loan balance = 0, manually delete task")

        prev_interest_time = self.interest_last_added  if self.interest_last_added  else self.created
        if (datetime.now(pytz.utc) - prev_interest_time) < self.interest_interval:
            return

        # interest_ammount = np.round(self.interest_rate * self.balance, 2)
        interest_ammount = self.interest_rate * self.balance
        LOGGER.info(
            "Accrue interest {} from {} to {}".format(
                interest_ammount, self.recipient, self.lender
            )
        )
        self.balance = self.balance + interest_ammount
        self.interest_last_added = datetime.now(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        self.save()

    def repay_loan(self, ammount):
        if ammount > self.balance:
            ammount = self.balance
        if ammount <= 0:
            return

        LOGGER.info(f"Repay {ammount} for {self.pk}")

        # Will throw an exception if not possible
        self.recipient.transfer_cash_to(self.lender, ammount)

        self.balance = self.balance - ammount
        self.save()


@receiver(pre_save, sender=Loan)
def create_loan(sender, instance, **kwargs):
    """ Pay execute trade upon creation """
    if instance.pk is None:
        instance.create_loan()


def apply_all_interest():
    """ Need to run this every week at some time e.g. 2am """
    loans = Loan.objects.all().filter(balance__gt=0)

    for loan in loans:
        loan.accrue_interest()