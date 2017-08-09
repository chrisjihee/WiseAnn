# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from WiseAnn import *
from WiseAnn.settings import *
from WiseAnn.views import *
from ZA.models import *

guide = dict()
guide["ZA"] = "ZA 태스크를 위한 텍스트가 준비되어 있습니다. 태스크를 진행할 텍스트를 선택하세요."


@never_cache
def index(request):
    user = auth_user(request)
    print(">>>>>(1)", user)
    msg = "user is none" if user is None else "user is user"
    if user is not None:
        texts1 = [x.text.textname for x in user.task_set.filter(finished=False)]
        texts2 = [x.text.textname for x in user.task_set.filter(finished=True)]
        progress = float(len(texts2)) / (len(texts1) + len(texts2)) * 100
        print(">>>>>(2)", len(texts1))
        print(">>>>>(2)", progress)
        # return JsonResponse({"status": 200, "msg": "OK -- OK?"})
        return render(request, 'ZA.html', {"guide": guide["ZA"] + msg,
                                           "texts_not_finished": texts1,
                                           "texts_finished": texts2,
                                           "progress": progress})
    else:
        return render(request, 'ZA.html', {"guide": guide["ZA"] + msg})


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
