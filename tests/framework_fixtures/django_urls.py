from django.urls import path

from .django_article_view import django_article_view
from .django_root_view import django_root_view

urlpatterns = [
    path("api/", django_root_view),
    path("api/articles/<str:article_id>", django_article_view),
]
