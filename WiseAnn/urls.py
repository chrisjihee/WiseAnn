# -*- coding: utf-8 -*-
"""WiseAnn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.http import *
from django.shortcuts import render

from WiseAnn import views

guide = dict()
guide["index"] = "WiseAnn 시스템에 오신 것을 환영합니다. 아래의 태스크에 대한 Annotation Workbench가 준비되어 있습니다."
guide["login"] = "WiseAnn을 사용하기 위해서 사용자 로그인이 필요합니다. 관리자로부터 허가된 사용자 정보로 로그인하세요."

urlpatterns = [
    # User visit
    url(r'^$', lambda x: render(x, 'index.html', {"guide": guide["index"]}), name='index'),
    url(r'^login/$', lambda x: render(x, 'login.html', {"guide": guide["login"]}), name='login'),
    # System call
    url(r'^api/login/', views.login, name='api_login'),
    # Sub app
    url(r'^ZA/', include('ZA.urls', namespace='ZA'), name='ZA'),
    url(r'^admin/', admin.site.urls, name='admin'),
]
