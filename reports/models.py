from django.db import models

class Reports(models.Model):
    website = models.CharField(max_length=50)
    failed = models.IntegerField()
    successful = models.IntegerField()
    duplicates = models.IntegerField()
    fee = models.IntegerField()
    createdAt = models.DateTimeField(auto_now_add=True)