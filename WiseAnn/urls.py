# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import render

guide = dict()
guide["index"] = "WiseAnn 시스템에 오신 것을 환영합니다. 아래의 태스크에 대한 Annotation Workbench가 준비되어 있습니다."

urlpatterns = [
    # User call
    url(r'^$', lambda x: render(x, 'index.html', {"guide": guide["index"]}), name='index'),
    # Sub apps
    url(r'^ZA/', include('ZA.urls')),
    url(r'^auth/', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls, name='admin')
]
