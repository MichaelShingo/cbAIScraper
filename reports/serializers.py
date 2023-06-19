from rest_framework import serializers
from .models import Reports

class ReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        fields = [
            'website',
            'failed',
            'successful',
            'duplicates',
            'fee',
            'createdAt',
        ]