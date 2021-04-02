from django.db import models
from polymorphic.models import PolymorphicModel
from django.db.models import Q

class Asset(PolymorphicModel):
    """
    Something that can be traded
    """

class Share(Asset):

    athlete = models.ForeignKey('Athlete', on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=10, decimal_places=2, default="0.0")
    owner = models.ForeignKey('Entity', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.volume = round(self.volume, 2)
        super(Share, self).save(*args, **kwargs)

    def __str__(self):
        return f"({self.athlete})/{self.volume}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def vol_for_athlete_entity(athlete, entity):
        shares = Share.objects.all().filter(Q(athlete=athlete) & Q(owner=entity))
        vol = sum([s.volume for s in shares]) if shares else 0.0
        return vol