"""
Serializers for kurs APIs
"""
from rest_framework import serializers

from course.models import (
    Kurs,
    Material,
)

class MaterialSerializer(serializers.ModelSerializer):
    """Serializer for materials."""

    class Meta:
        model = Material
        fields = ['id', 'name', 'video']
        read_only_fields = ['id']

class KursSerializer(serializers.ModelSerializer):
    """Serializer for kurses."""
    materials = MaterialSerializer(many=True, required=False)
    class Meta:
        model = Kurs
        fields = ['id', 'author', 'title', 'description', 'price', 'link', 'materials']
        read_only_fields = ['id']

    def _get_or_create_materials(self, materials, kurs):
        """Handle getting or creating materials as needed."""
        auth_user = self.context['request'].user
        for material in materials:
            material_obj, created = Material.objects.get_or_create(
                user=auth_user,
                **material,
            )
            kurs.materials.add(material_obj)

    def create(self, validated_data):
        """Create a kurs."""
        materials = validated_data.pop('materials', [])
        kurs = Kurs.objects.create(**validated_data)
        self._get_or_create_materials(materials, kurs)

        return kurs

    def update(self, instance, validated_data):
        """Update kurs."""
        materials = validated_data.pop('materials', None)
        if materials is not None:
            instance.materials.clear()
            self._get_or_create_materials(materials, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class KursDetailSerializer(KursSerializer):
    """Serializer for kurs detail view."""

    class Meta(KursSerializer.Meta):
        fields = KursSerializer.Meta.fields + ['description']



