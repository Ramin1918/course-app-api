from django.urls import (
    path,
    include,
)
from course import views

urlpatterns = [
    path('index', views.index, name="index"),
]
