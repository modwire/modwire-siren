from django.urls import path

from .django_article_view import django_article_view

urlpatterns = [path("api/articles/<str:article_id>", django_article_view)]
