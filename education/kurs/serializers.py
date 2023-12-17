"""
Serializers for kurs APIs
"""
from rest_framework import serializers

from course.models import Kurs


class KursSerializer(serializers.ModelSerializer):
    """Serializer for kurseses."""

    class Meta:
        model = Kurs
        fields = ['id', 'title', 'description', 'price', 'link']
        read_only_fields = ['id']
