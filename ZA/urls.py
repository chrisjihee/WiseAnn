from django.conf.urls import url
from django.shortcuts import render

from ZA import views

urlpatterns = [
    # User visit
    url(r'^$', views.index, name='index'),
    # System call
    url(r'^api/reset/', views.reset, name='reset'),
]
