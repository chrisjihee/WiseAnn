# -*- coding: utf-8 -*-
from django.conf.urls import url

from ZA import views

urlpatterns = [
    # Page view
    url(r'^$', views.index, name='index'),
    # System call
    url(r'^api/reset/', views.reset, name='reset'),
]
