# Create your models here.
from django.db import models


class KG(models.Model):
    kg_name = models.CharField(max_length=1000, primary_key=True)


class Label(models.Model):
    kg_name = models.ForeignKey(KG, on_delete=models.CASCADE)
    label_name = models.CharField(max_length=1000)


class Relation(models.Model):
    kg_name = models.ForeignKey(KG, on_delete=models.CASCADE)
    relation_name = models.CharField(max_length=1000)
