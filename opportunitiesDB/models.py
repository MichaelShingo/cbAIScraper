from django.db import models
from django.contrib.postgres.fields import ArrayField

class ActiveOpps(models.Model):
    title = models.CharField(max_length=150)
    deadline = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=150)
    description = models.TextField()
    link = models.CharField()
    typeOfOpp = ArrayField(models.CharField(max_length=75))
    approved = models.BooleanField()
    keywords = ArrayField(models.CharField(max_length=75))
    websiteName = models.CharField(max_length=150)
    createdAt = models.DateTimeField(auto_now_add=True)
