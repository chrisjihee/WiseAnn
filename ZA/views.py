# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict

from pandas import read_excel
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
def export(request, username):
    print("[INIT] export")
    print("=" * 100)
    print(" Data Export : %s" % username)
    print("=" * 100)

    # 42maru = A1 + A2 + B1 + B3
    # knue = A1 + B1 + B2 + C + D
    user_files = {
        "42maru": [f for f in list_files("/WorkData/LangEval/WiseAnnData/data") if "A1" in f or "A2" in f or "B1" in f or "B3" in f],
        "knue": [f for f in list_files("/WorkData/LangEval/WiseAnnData/data") if "A1" in f or "B1" in f or "C" in f or "D" in f],
    }
    if username in user_files:
        num_pass = 0
        num_fail = 0
        passed_texts = OrderedDict()
        failed_texts = []
        files = user_files[username]
        outdir = "/WorkData/LangEval/WiseAnnData/result_" + username
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        for x in [x for x in Task.objects.all() if x.user.username != "ZA.chrisjihee@etri.re.kr"]:
            if x.relations != "{}":
                rels = json.loads(x.relations, object_pairs_hook=OrderedDict)
                fs = [f for f in files if x.text.textname in f]
                if len(fs) != 1:
                    num_fail += 1
                    failed_texts.append(x.text.textname)
                    print("[FAIL] %s" % x.text.textname)
                    continue
                fname = os.path.basename(fs[0])
                doc = json.load(open(fs[0]), object_pairs_hook=OrderedDict)
                num_valid_za = 0

                for si, zas in rels.items():
                    si = int(si)
                    zi = 0
                    doc["sentence"][si]["ZA"] = list()
                    for za in sorted(zas.values(), key=lambda zz: zz["head_wid"] * 1000000000 + zz["ant_sid"] * 1000000 + zz["ant_wid"] * 1000000):
                        if za["valid"]:
                            doc["sentence"][si]["ZA"].append(clone_tagged_za(za, zi))
                            zi += 1
                            num_valid_za += 1

                json.dump(doc, open(os.path.join(outdir, fname), "w"))
                print("[PASS] \t%s\t~~~>\t%d" % (x.text.textname, num_valid_za))
                passed_texts[x.text.textname] = num_valid_za
                num_pass += 1

        print("[EXIT] export")
        return JsonResponse({"status": 200, "msg": "OK", "username": username,
                             "num_pass": num_pass, "passed_texts": passed_texts,
                             "num_fail": num_fail, "failed_texts": failed_texts}, status=200)
    else:
        print("[FAIL] %s : %s" % ("Invalid username", username))
        print("[EXIT] export")
        return JsonResponse({"status": 400, "msg": "Invalid username", "username": username}, status=400)


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


def reset_tasks(filename=os.path.join(BASE_DIR, "data/tasks.xlsx")):
    data = read_excel(filename)
    num = 0
    for x in Task.objects.all():
        x.delete()
    for x in User.objects.all():
        _, annotator = x.username.split(".")
        textnames1 = [(data.ix[i]["filename"].split(".")[0], data.ix[i]["finished1"]) for i in range(len(data)) if data.ix[i]["annotator1"] == annotator]
        textnames2 = [(data.ix[i]["filename"].split(".")[0], data.ix[i]["finished2"]) for i in range(len(data)) if data.ix[i]["annotator2"] == annotator]
        textnames = dict(textnames1 + textnames2)
        for y in Text.objects.all():
            if y.textname in textnames:
                Task(user=x, text=y, finished=textnames[y.textname]).save()
                num += 1
    print(">>> [ZA.views.reset_tasks] Insert: %d tasks" % num)
    return num
