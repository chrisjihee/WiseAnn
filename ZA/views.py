# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict

import django.contrib.auth as auth
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from pandas import read_excel

from WiseAnn import *
from WiseAnn.json2 import WiseJson
from WiseAnn.settings import *
from ZA.models import *

guide = dict()
guide["ZA_not_user"] = "로그인된 사용자 정보가 없습니다."
guide["ZA_yet_list"] = "ZA 태스크를 위한 텍스트가 준비되어 있지 않습니다. 관리자에게 문의하시기 바랍니다."
guide["ZA_yes_list"] = "ZA 태스크를 위한 텍스트가 준비되어 있습니다. 태스크를 진행할 텍스트를 선택하세요."
guide["ZA_not_text"] = "잘못된 이름의 문서입니다. URL을 확인해주세요."
guide["ZA_not_task"] = "현재 사용자에게 할당되지 않은 문서입니다. URL을 확인해주세요."
guide["ZA_yes_task"] = "로딩된 문서에 대한 Annotation 태스크를 시작합니다. ZA 현상이 있는 부분을 가이드에 따라 태깅하세요."


def set_for_utf8():
    import sys
    reload(sys)
    sys.setdefaultencoding("utf8")


set_for_utf8()


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
            text = json.load(open(filename))
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


def list_files(indir, keyword=None):
    for (path, _, files) in sorted(os.walk(indir)):
        for f in sorted(files):
            if keyword is None or keyword in f:
                yield os.path.join(path, f)


def clone_tagged_za(za1, zi):
    za2 = OrderedDict()
    za2["id"] = zi
    za2["type"] = za1["type"]
    za2["head_wid"] = za1["head_wid"]
    za2["ant_sid"] = za1["ant_sid"]
    za2["ant_wid"] = za1["ant_wid"]
    za2["ant_is_title"] = za1["ant_is_title"]
    za2["weight"] = 1.01
    return za2


@csrf_exempt
def export(request, username, datadir=os.path.join(BASE_DIR, "data/")):
    print("[INIT] export")
    print("=" * 100)
    print(" Data Export : %s" % username)
    print("=" * 100)

    tasks = read_excel(os.path.join(datadir, "tasks.xlsx"))
    textnames = [tasks.ix[i]["filename"].split(".")[0] for i in range(len(tasks)) if tasks.ix[i]["ZA.annotator1"] == username] + \
                [tasks.ix[i]["filename"].split(".")[0] for i in range(len(tasks)) if tasks.ix[i]["ZA.annotator2"] == username]
    if len(textnames) == 0:
        print("[FAIL] %s : %s" % ("Invalid username", username))
        print("[EXIT] export")
        return JsonResponse({"status": 400, "msg": "Invalid username", "username": username}, status=400)
    outdir1 = os.path.join(datadir + "result", username)
    if not os.path.isdir(outdir1):
        os.makedirs(outdir1)
    outdir2 = os.path.join(datadir + "tags", username)
    if not os.path.isdir(outdir2):
        os.makedirs(outdir2)

    num_pass = 0
    num_fail = 0
    for x in [x for x in Task.objects.all() if x.user.username.replace("ZA.guest@home.kr", "ZA.42maru") == username]:
        if x.relations != "{}":
            fs = [f for f in textnames if x.text.textname in f]
            if len(fs) != 1:
                num_fail += 1
                print("[FAIL] %s" % x.text.textname)
                continue
            fname = os.path.basename(fs[0])

            doc = json.load(open(os.path.join(datadir + "texts", fname + ".json")), object_pairs_hook=OrderedDict)
            ents = json.loads(x.entities, object_pairs_hook=OrderedDict)
            rels = json.loads(x.relations, object_pairs_hook=OrderedDict)
            json.dump(ents, open(os.path.join(outdir2, fname + ".entities"), "w"), ensure_ascii=False, indent=2)
            json.dump(rels, open(os.path.join(outdir2, fname + ".relations"), "w"), ensure_ascii=False, indent=2)

            num_valid = 0
            for si, zas in rels.items():
                si = int(si)
                zi = 0
                try:
                    doc["sentence"][si]["ZA"] = list()
                except Exception as e:
                    print("[ERROR1] \t%s\t~~~>\t%d" % (x.text.textname, num_valid))
                    print(e)

                for za in sorted(zas.values(), key=lambda zz: zz["head_wid"] * 1000000000 + zz["ant_sid"] * 1000000 + zz["ant_wid"] * 1000000):
                    if za["valid"]:
                        try:
                            doc["sentence"][si]["ZA"].append(clone_tagged_za(za, zi))
                        except Exception as e:
                            print("[ERROR2] \t%s\t~~~>\t%d" % (x.text.textname, num_valid))
                            print(e)

                        zi += 1
                        num_valid += 1

            json.dump(doc, open(os.path.join(outdir1, fname + ".json"), "w"), ensure_ascii=False, indent=4, cls=WiseJson)
            print("[PASS] \t%s\t~~~>\t%d" % (x.text.textname, num_valid))
            num_pass += 1

    print("[EXIT] export")
    return JsonResponse({"status": 200, "msg": "OK", "username": username, "num_pass": num_pass, "num_fail": num_fail}, status=200)


@csrf_exempt
def append(request):
    if request.POST.has_key("password") and request.POST["password"] == TRUTH:
        return JsonResponse({"status": 200, "msg": "OK", "num_texts": append_texts(), "num_tasks": append_tasks()}, status=200)
    else:
        return JsonResponse({"status": 401, "msg": "Unauthorized"}, status=401)


@csrf_exempt
def reset(request):
    if request.POST.has_key("password") and request.POST["password"] == TRUTH:
        return JsonResponse({"status": 200, "msg": "OK", "num_users": reset_users(), "num_texts": reset_texts(), "num_tasks": reset_tasks()}, status=200)
    else:
        return JsonResponse({"status": 401, "msg": "Unauthorized"}, status=401)


def reset_users(datadir=os.path.join(BASE_DIR, "data/")):
    users = json.load(open(os.path.join(datadir, "users.json")))
    num = 0
    for x in User.objects.all():
        x.delete()
    for x in users:
        User(app=x["app"],
             level=x["level"],
             username=x["username"],
             password=x["password"],
             fullname=x["fullname"],
             telephone=x["telephone"]).save()
        num += 1
    print(">>> [ZA.views.reset_users] Insert: %d users" % num)
    return num


def append_texts(datadir=os.path.join(BASE_DIR, "data/")):
    texts = sorted(os.listdir(os.path.join(datadir, "texts")))
    num = 0
    prev = [x.textname for x in Text.objects.all()]
    for x in texts:
        if x.split(".")[0] not in prev:
            Text(textname=x.split(".")[0]).save()
            num += 1
    print(">>> [ZA.views.append_texts] Insert: %d texts" % num)
    return num


def reset_texts(datadir=os.path.join(BASE_DIR, "data/")):
    texts = sorted(os.listdir(os.path.join(datadir, "texts")))
    num = 0
    for x in Text.objects.all():
        x.delete()
    for x in texts:
        Text(textname=x.split(".")[0]).save()
        num += 1
    print(">>> [ZA.views.reset_texts] Insert: %d texts" % num)
    return num


def append_tasks(datadir=os.path.join(BASE_DIR, "data/")):
    tasks = read_excel(os.path.join(datadir, "tasks.xlsx"))
    num = 0
    for x in User.objects.all():
        tagsdir = os.path.join(datadir + "tags", x.username)
        textnames = [(tasks.ix[i]["filename"].split(".")[0], tasks.ix[i]["ZA.finished1"]) for i in range(len(tasks)) if tasks.ix[i]["ZA.annotator1"] == x.username] + \
                    [(tasks.ix[i]["filename"].split(".")[0], tasks.ix[i]["ZA.finished2"]) for i in range(len(tasks)) if tasks.ix[i]["ZA.annotator2"] == x.username]
        textnames = dict(textnames)
        for y in Text.objects.all():
            if y.textname in textnames:
                q = Task.objects.filter(user=User.objects.get(username=x.username), text=Text.objects.get(textname=y.textname))
                if not q.exists():
                    tagfile1 = os.path.join(tagsdir, y.textname + ".entities")
                    tagfile2 = os.path.join(tagsdir, y.textname + ".relations")
                    if os.path.isfile(tagfile1) and os.path.isfile(tagfile2):
                        tags1 = open(tagfile1).read()
                        tags2 = open(tagfile2).read()
                        Task(user=x, text=y, finished=textnames[y.textname], entities=tags1, relations=tags2).save()
                        num += 1
                    else:
                        Task(user=x, text=y, finished=textnames[y.textname]).save()
                        num += 1
    print(">>> [ZA.views.append_tasks] Insert: %d tasks" % num)
    return num


def reset_tasks(datadir=os.path.join(BASE_DIR, "data/")):
    tasks = read_excel(os.path.join(datadir, "tasks.xlsx"))
    num = 0
    for x in Task.objects.all():
        x.delete()
    for x in User.objects.all():
        tagsdir = os.path.join(datadir + "tags", x.username)
        textnames = [(tasks.ix[i]["filename"].split(".")[0], tasks.ix[i]["ZA.finished1"]) for i in range(len(tasks)) if tasks.ix[i]["ZA.annotator1"] == x.username] + \
                    [(tasks.ix[i]["filename"].split(".")[0], tasks.ix[i]["ZA.finished2"]) for i in range(len(tasks)) if tasks.ix[i]["ZA.annotator2"] == x.username]
        textnames = dict(textnames)
        for y in Text.objects.all():
            if y.textname in textnames:
                tagfile1 = os.path.join(tagsdir, y.textname + ".entities")
                tagfile2 = os.path.join(tagsdir, y.textname + ".relations")
                if os.path.isfile(tagfile1) and os.path.isfile(tagfile2):
                    tags1 = open(tagfile1).read()
                    tags2 = open(tagfile2).read()
                    Task(user=x, text=y, finished=textnames[y.textname], entities=tags1, relations=tags2).save()
                    num += 1
                else:
                    Task(user=x, text=y, finished=textnames[y.textname]).save()
                    num += 1
    print(">>> [ZA.views.reset_tasks] Insert: %d tasks" % num)
    return num
