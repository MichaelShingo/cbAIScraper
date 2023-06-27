from rest_framework import serializers
from .models import ActiveOpps

class ActiveOppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveOpps
        fields = [
            'id',
            'title',
            'titleAI',
            'deadline',
            'location',
            'description',
            'link',
            'typeOfOpp',
            'approved',
            'keywords',
            'websiteName',
            'createdAt',
        ]