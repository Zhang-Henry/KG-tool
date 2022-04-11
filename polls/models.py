# Create your models here.
from django.db import models


class KG(models.Model):
    name = models.CharField(max_length=1000, primary_key=True)
    date = models.CharField(max_length=100)
    type = models.CharField(max_length=100)

class Label(models.Model):
    kg = models.ForeignKey(KG, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)


class Relation(models.Model):
    kg = models.ForeignKey(KG, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
