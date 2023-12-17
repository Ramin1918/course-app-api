"""
Views for the kurs APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from course.models import Kurs
from kurs import serializers


class KursViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.KursDetailSerializer
    queryset = Kurs.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve kurses for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.KursSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new kurs."""
        serializer.save(user=self.request.user)
