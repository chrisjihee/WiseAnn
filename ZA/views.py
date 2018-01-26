# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import django.contrib.auth as auth
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from WiseAnn.settings import *
from ZA.models import *

guide = dict()
guide["ZA_not_user"] = "로그인된 사용자 정보가 없습니다."
guide["ZA_yet_list"] = "ZA 태스크를 위한 텍스트가 준비되어 있지 않습니다. 관리자에게 문의하시기 바랍니다."
guide["ZA_yes_list"] = "ZA 태스크를 위한 텍스트가 준비되어 있습니다. 태스크를 진행할 텍스트를 선택하세요."
guide["ZA_not_text"] = "잘못된 이름의 문서입니다. URL을 확인해주세요."
guide["ZA_not_task"] = "현재 사용자에게 할당되지 않은 문서입니다. URL을 확인해주세요."
guide["ZA_yes_task"] = "로딩된 문서에 대한 Annotation 태스크를 시작합니다. ZA 현상이 있는 부분을 가이드에 따라 태깅하세요."


@never_cache
def index(request):
    user = auth.get_user(request)
    if user.username == "":
        return render(request, 'message.html', {"guide": guide["ZA_not_user"]})

    q = User.objects.filter(username=user)
    if not q.exists():
        return render(request, 'message.html', {"guide": guide["ZA_yet_list"]})

    user = q.first()
    tasks = user.task_set
    yes = [x.text.textname for x in tasks.filter(finished=True)]
    yet = [x.text.textname for x in tasks.filter(finished=False)]
    progress = float(len(yes)) / (len(yes) + len(yet)) * 100
    texts_yes_finished = [{"i": i + 1, "name": x, "label": x} for (i, x) in enumerate(yes)]
    texts_yet_finished = [{"i": i + 1, "name": x, "label": x} for (i, x) in enumerate(yet)]
    return render(request, 'ZA/list.html', {"guide": guide["ZA_yes_list"], "progress": progress,
                                            "texts_yes_finished": texts_yes_finished,
                                            "texts_yet_finished": texts_yet_finished})


@never_cache
def task(request, textname):
    user = auth.get_user(request)
    if user.username == "":
        return render(request, 'message.html', {"guide": guide["ZA_not_user"]})

    q = User.objects.filter(username=user)
    if not q.exists():
        return render(request, 'message.html', {"guide": guide["ZA_yet_list"]})

    user = q.first()
    q = Text.objects.filter(textname=textname)
    if not q.exists():
        return render(request, 'message.html', {"guide": guide["ZA_not_text"]})

    text = q.first()
    q = Task.objects.filter(user=user, text=text)
    if not q.exists():
        return render(request, 'message.html', {"guide": guide["ZA_not_task"]})

    task = q.first()
    textname = text.textname
    textcont = read_text(textname)
    return render(request, 'ZA/task.html', {"title": "[Title]",
                                            "textname": textname,
                                            "textcont": textcont,
                                            "textcont2": json.dumps(textcont),
                                            "entities": task.entities,
                                            "relations": task.relations})


@csrf_exempt
@never_cache
def save(request, textname):
    if "entities" not in request.POST or "relations" not in request.POST:
        return JsonResponse({"status": 400, "msg": "Not Tagging"}, status=400)

    user = auth.get_user(request)
    if user.username == "":
        return JsonResponse({"status": 401, "msg": "Not User"}, status=401)

    q = User.objects.filter(username=user)
    if not q.exists():
        return JsonResponse({"status": 403, "msg": "Not Assigned"}, status=403)

    user = q.first()
    q = Text.objects.filter(textname=textname)
    if not q.exists():
        return JsonResponse({"status": 404, "msg": "Not Text"}, status=404)

    text = q.first()
    q = Task.objects.filter(user=user, text=text)
    if not q.exists():
        return JsonResponse({"status": 402, "msg": "Not Task"}, status=402)

    task = q.first()
    ents = request.POST.get("entities")
    rels = json.loads(request.POST.get("relations"))
    rels2 = {}
    for i in map(lambda x: str(x), sorted(map(lambda x: int(x), rels.keys()))):
        sid = int(i)
        zid = 0
        rels2[sid] = {}
        for j in map(lambda x: str(x), sorted(map(lambda x: int(x), rels[i].keys()))):
            if "valid" not in rels[i][j] or rels[i][j]["valid"] is True:
                rels2[sid][zid] = rels[i][j]
                rels2[sid][zid]["id"] = zid
                zid += 1
    rels = json.dumps(rels2)
    task.entities = ents
    task.relations = rels
    task.save()
    return JsonResponse({"status": 200, "msg": "OK", "function": "save"}, status=200)


def read_text(textname, dirname=os.path.join(BASE_DIR, "data/texts")):
    if os.path.isdir(dirname):
        filename = os.path.join(dirname, textname + ".json")
        if os.path.isfile(filename):
            text = json.load(open(filename, encoding='utf8'))
            for sent in text["sentence"]:
                for word in sent["dependency"]:
                    if word["label"].startswith("N"):
                        word["label_color"] = "forestgreen"
                    elif word["label"].startswith("V"):
                        word["label_color"] = "deepskyblue"
                    else:
                        word["label_color"] = "darkslategray"
            return text
    return None
