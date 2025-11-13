# devices/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('collect/', views.collect_once, name='collect_once'),
]
