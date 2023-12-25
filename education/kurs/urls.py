"""
URL mappings for the kurs app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from kurs import views


router = DefaultRouter()
router.register('kurses', views.KursViewSet)
router.register('materials', views.MaterialViewSet)

app_name = 'kurs'

urlpatterns = [
    path('', include(router.urls)),
]
