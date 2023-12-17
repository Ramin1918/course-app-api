"""
Serializers for kurs APIs
"""
from rest_framework import serializers

from course.models import Kurs


class KursSerializer(serializers.ModelSerializer):
    """Serializer for kurses."""

    class Meta:
        model = Kurs
        fields = ['id', 'author', 'title', 'description', 'price', 'link']
        read_only_fields = ['id']


class KursDetailSerializer(KursSerializer):
    """Serializer for kurs detail view."""

    class Meta(KursSerializer.Meta):
        fields = KursSerializer.Meta.fields + ['description']
