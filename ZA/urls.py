# -*- coding: utf-8 -*-
from django.conf.urls import url

from ZA import views

urlpatterns = [
    # User call
    url(r'^$', views.index, name='index'),
    url(r'^(?P<textname>[^/]+)$', views.task, name='task_view'),
    url(r'^(?P<textname>[^/]+)/save/', views.save, name='task_save'),
]
