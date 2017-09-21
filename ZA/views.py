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
guide["ZA_task"] = "로딩된 문서에 대한 Annotation 태스크를 시작합니다. ZA 현상이 있는 부분을 가이드에 따라 태깅하세요."
guide["ZA_no_task"] = "존재하지 않는 문서입니다. 이전 페이지로 돌아가세요."
guide["ZA_no_user"] = "로그인 정보가 없습니다. 페이지를 다시 로드하세요."


def read_text(textname, dirname=os.path.join(BASE_DIR, "data/texts")):
    if os.path.isdir(dirname):
        filename = os.path.join(dirname, textname + ".ann.json")
        if os.path.isfile(filename):
            data = open(filename).read()
            text = json.loads(data)
            for sent in text["sents"]:
                for word in sent["words"]:
                    if word["label"].startswith("N"):
                        word["label_color"] = "forestgreen"
                    elif word["label"].startswith("V"):
                        word["label_color"] = "deepskyblue"
                    else:
                        word["label_color"] = "darkslategray"
            return text
    return None


@never_cache
def task(request, textname):
    print("textname = " + textname)
    user = auth_user(request)
    print(">>>>>(1)", user)
    print(">>>>>(2.1)")
    print(textname)
    print(">>>>>(2.2)")
    msg = "user is none" if user is None else "user is user"
    print(">>>>>(3.0)")
    if user is not None:
        print(">>>>>(3)")
        try:
            print(">>>>>(3.1)")
            text = Text.objects.get(textname=textname)
            textname = text.textname
            print(">>>>>(3.1.5)")
            textcont = read_text(textname)
            # print(textcont)
            print(">>>>>(3.2)")
            task = Task.objects.get(user=user, text=text)
            # print(task.entities)
            return render(request, 'ZA_task.html', {"guide": guide["ZA_task"] + msg,
                                                    "title": "[Title]",
                                                    "textname": textname,
                                                    "textcont": textcont,
                                                    "textcont2": json.dumps(textcont),
                                                    "entities": task.entities,
                                                    "relations": task.relations})
        except (KeyError, Text.DoesNotExist):
            return render(request, 'ZA_task.html', {"guide": guide["ZA_no_task"] + msg})
    else:
        print(">>>>>(3.x)")
        return render(request, 'ZA_task.html', {"guide": guide["ZA_no_user"] + msg})


@csrf_exempt
@need_auth
@never_cache
def save(request, textname):
    print("=" * 80)
    print(" * save(request, textname)")
    print("=" * 80)
    print(" - textname = " + textname)
    print(" - request = ", request)
    user = auth_user(request)
    print(" - user = ")
    print(user)
    entities = request.POST.get("entities")
    rels = json.loads(request.POST.get("relations"))
    relations = {}
    for i in map(lambda x: str(x), sorted(map(lambda x: int(x), rels.keys()))):
        sid = int(i)
        zid = 0
        relations[sid] = {}
        for j in map(lambda x: str(x), sorted(map(lambda x: int(x), rels[i].keys()))):
            if "valid" not in rels[i][j] or rels[i][j]["valid"]:
                relations[sid][zid] = rels[i][j]
                relations[sid][zid]["id"] = zid
                zid += 1
    print(" - entities = ")
    print(json.dumps(entities))
    print(" - relations = ")
    print(json.dumps(relations))

    # User.objects.get(username=username, password=password)
    text = Text.objects.get(textname=textname)
    print(" - text = ")
    print(text)
    task = Task.objects.get(user=user, text=text)
    print(" - task = ")
    print(task)
    task.entities = entities
    task.relations = json.dumps(relations)
    task.save()
    return JsonResponse({"status": 200, "msg": "OK",
                         "function": "save"}, status=200)


@never_cache
def index(request):
    user = auth_user(request)
    print(">>>>>(1)", user)
    msg = "user is none" if user is None else "user is user"
    if user is not None:
        yes = [x.text.textname for x in user.task_set.filter(finished=True)]
        yet = [x.text.textname for x in user.task_set.filter(finished=False)]
        progress = float(len(yes)) / (len(yes) + len(yet)) * 100
        texts_yes_finished = [{"i": i + 1, "name": x, "label": x} for (i, x) in enumerate(yes)]
        texts_yet_finished = [{"i": i + 1, "name": x, "label": x} for (i, x) in enumerate(yet)]
        return render(request, 'ZA_index.html', {"guide": guide["ZA"] + msg,
                                                 "progress": progress,
                                                 "texts_yes_finished": texts_yes_finished,
                                                 "texts_yet_finished": texts_yet_finished})
        # return JsonResponse({"status": 200, "msg": "OK -- OK?"})
    else:
        return render(request, 'ZA_index.html', {"guide": guide["ZA_no_user"] + msg})


@csrf_exempt
def reset(request):
    if request.POST.has_key("password") and request.POST["password"] == TRUTH:
        return JsonResponse({"status": 200, "msg": "OK",
                             "num_users": reset_users(),
                             "num_texts": reset_texts(),
                             "num_tasks": reset_tasks()}, status=200)
    else:
        return JsonResponse({"status": 401, "msg": "Unauthorized"}, status=401)


def reset_users(filename=os.path.join(BASE_DIR, "data/users.json")):
    num = 0
    if os.path.isfile(filename):
        for x in User.objects.all():
            x.delete()
        data = open(filename).read()
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
        print(">>> [ZA.views.reset_users] No file: %s" % filename)
    return num


def reset_texts(dirname=os.path.join(BASE_DIR, "data/texts")):
    num = 0
    if os.path.isdir(dirname):
        for x in Text.objects.all():
            x.delete()
        for x in sorted(os.listdir(dirname)):
            Text(textname=x.split(".")[0]).save()
            num += 1
        print(">>> [ZA.views.reset_texts] Insert: %d texts" % num)
    else:
        print(">>> [ZA.views.reset_texts] No dir: %s" % dirname)
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
