from django.urls import path
from . import views

urlpatterns = [
    path("dynamic-crawl/", views.dynamic_crawl, ),
]
