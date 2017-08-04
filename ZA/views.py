# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import *
from django.shortcuts import render
from django.views.decorators.csrf import *
from WiseAnn.settings import *

from WiseAnn import *
from ZA import *
from ZA.models import *
import json


def index(request):
    return HttpResponse("This is ZA annotation page")


@csrf_exempt
def reset(request):
    if request.POST.has_key("password") and request.POST["password"] == TRUTH:
        return JsonResponse({"status": 200, "msg": "OK",
                             "num_users": reset_users(),
                             "num_texts": reset_texts(),
                             "num_tasks": reset_tasks()}, status=200)
    else:
        return JsonResponse({"status": 401, "msg": "Unauthorized"}, status=401)


def reset_users(file=os.path.join(BASE_DIR, "data/users.json")):
    num = 0
    if os.path.isfile(file):
        for x in User.objects.all():
            x.delete()
        data = open(file).read()
        for x in json.loads(data):
            User(app=x["app"],
                 level=x["level"],
                 username=x["username"],
                 password=x["password"],
                 fullname=x["fullname"],
                 telephone=x["telephone"]).save()
            num += 1
        print(">>> [ZA.views.reset_users] Insert: %d users" % num)
    else:
        print(">>> [ZA.views.reset_users] No file: %s" % file)
    return num


def reset_texts(dir=os.path.join(BASE_DIR, "data/texts")):
    num = 0
    if os.path.isdir(dir):
        for x in Text.objects.all():
            x.delete()
        for x in sorted(os.listdir(dir)):
            Text(textname=x.replace(".txt", "")).save()
            num += 1
        print(">>> [ZA.views.reset_texts] Insert: %d texts" % num)
    else:
        print(">>> [ZA.views.reset_texts] No dir: %s" % dir)
    return num


def reset_tasks():
    num = 0
    for x in Task.objects.all():
        x.delete()
    for x in User.objects.all():
        for y in Text.objects.all():
            Task(user=x, text=y).save()
            num += 1
    print(">>> [ZA.views.reset_tasks] Insert: %d tasks" % num)
    return num
