from django.db import models
from user.models import User


class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='car')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"
