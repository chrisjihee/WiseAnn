# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import render

from WiseAnn import views

guide = dict()
guide["index"] = "WiseAnn 시스템에 오신 것을 환영합니다. 아래의 태스크에 대한 Annotation Workbench가 준비되어 있습니다."
guide["login"] = "WiseAnn을 사용하기 위해서 사용자 로그인이 필요합니다. 관리자로부터 허가된 사용자 정보로 로그인하세요."

urlpatterns = [
    # Page view
    url(r'^$', lambda x: render(x, 'index.html', {"guide": guide["index"]}), name='index'),
    url(r'^login/$', lambda x: render(x, 'login.html', {"guide": guide["login"]}), name='login'),
    # System call
    url(r'^api/login/', views.login, name='api_login'),
    # Sub apps
    url(r'^ZA/', include('ZA.urls', namespace='ZA'), name='ZA'),
    url(r'^admin/', admin.site.urls, name='admin'),
]
