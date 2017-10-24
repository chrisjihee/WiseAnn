# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict

from pandas import read_excel
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from WiseAnn.json2 import WiseJson
from WiseAnn import *
from WiseAnn.settings import *
from WiseAnn.views import *
from ZA.models import *

guide = dict()
guide["ZA"] = "ZA 태스크를 위한 텍스트가 준비되어 있습니다. 태스크를 진행할 텍스트를 선택하세요."
guide["ZA_task"] = "로딩된 문서에 대한 Annotation 태스크를 시작합니다. ZA 현상이 있는 부분을 가이드에 따라 태깅하세요."
guide["ZA_no_task"] = "존재하지 않는 문서입니다. 이전 페이지로 돌아가세요."
guide["ZA_no_user"] = "로그인 정보가 없습니다. 페이지를 다시 로드하세요."


def set_for_utf8():
    import sys
    reload(sys)
    sys.setdefaultencoding("utf8")


set_for_utf8()


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


@never_cache
def task(request, textname):
    user = auth_user(request)
    if user is not None:
        try:
            text = Text.objects.get(textname=textname)
            textname = text.textname
            textcont = read_text(textname)
            task = Task.objects.get(user=user, text=text)
            return render(request, 'ZA_task.html', {"guide": guide["ZA_task"],
                                                    "title": "[Title]",
                                                    "textname": textname,
                                                    "textcont": textcont,
                                                    "textcont2": json.dumps(textcont),
                                                    "entities": task.entities,
                                                    "relations": task.relations})
        except (KeyError, Text.DoesNotExist):
            return render(request, 'ZA_task.html', {"guide": guide["ZA_no_task"]})
    else:
        return render(request, 'ZA_task.html', {"guide": guide["ZA_no_user"]})


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
    if user is not None:
        yes = [x.text.textname for x in user.task_set.filter(finished=True)]
        yet = [x.text.textname for x in user.task_set.filter(finished=False)]
        progress = float(len(yes)) / (len(yes) + len(yet)) * 100
        texts_yes_finished = [{"i": i + 1, "name": x, "label": x} for (i, x) in enumerate(yes)]
        texts_yet_finished = [{"i": i + 1, "name": x, "label": x} for (i, x) in enumerate(yet)]
        return render(request, 'ZA_index.html', {"guide": guide["ZA"],
                                                 "progress": progress,
                                                 "texts_yes_finished": texts_yes_finished,
                                                 "texts_yet_finished": texts_yet_finished})
    else:
        return render(request, 'ZA_index.html', {"guide": guide["ZA_no_user"]})


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
                doc["sentence"][si]["ZA"] = list()
                for za in sorted(zas.values(), key=lambda zz: zz["head_wid"] * 1000000000 + zz["ant_sid"] * 1000000 + zz["ant_wid"] * 1000000):
                    if za["valid"]:
                        doc["sentence"][si]["ZA"].append(clone_tagged_za(za, zi))
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
