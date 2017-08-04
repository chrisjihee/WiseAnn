# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.shortcuts import render

from ZA import views

guide = dict()
guide["ZA"] = "ZA 태스크를 위한 텍스트가 준비되어 있습니다. 태스크를 진행할 텍스트를 선택하세요."

urlpatterns = [
    # Page view
    url(r'^$', lambda x: render(x, 'ZA.html', {"guide": guide["ZA"]}), name='ZA'),
    # System call
    url(r'^api/reset/', views.reset, name='reset'),
]
