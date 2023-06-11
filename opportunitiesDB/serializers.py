from rest_framework import serializers
from .models import ActiveOpps

class ActiveOppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveOpps
        fields = [
            'title',
            'deadline',
            'location',
            'description',
            'link',
            'typeOfOpp',
            'approved',
            'keywords'
        ]