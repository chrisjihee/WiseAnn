# -*- coding: utf-8 -*-
from django.conf.urls import url

from ZA import views

urlpatterns = [
    # Admin call
    url(r'^api/export/(?P<username>[^/]+)$', views.export, name='export'),
    # User call
    url(r'^$', views.index, name='index'),
    url(r'^(?P<textname>[^/]+)$', views.task, name='task_view'),
    url(r'^(?P<textname>[^/]+)/save/', views.save, name='task_save'),
]
