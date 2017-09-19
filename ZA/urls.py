# -*- coding: utf-8 -*-
from django.conf.urls import url

from ZA import views

urlpatterns = [
    # System call
    url(r'^api/reset/', views.reset, name='reset'),
    # Page view
    url(r'^$', views.index, name='index'),
    url(r'^(?P<textname>[^/]+)$', views.task, name='task_view'),
]
