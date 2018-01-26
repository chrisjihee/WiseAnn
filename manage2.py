import os
from collections import OrderedDict

import django
from django.http import JsonResponse
from pandas import read_excel, isnull, json

from WiseAnn.json2 import WiseJson
from common.io import list_files
from common.task import Task as MyTask


def check():
    print("[Django Check]")
    print("  Path: {}".format(django.__path__[0]))
    print("  Version: {}".format(django.__version__))
    print()


def load():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WiseAnn.settings")
    django.setup(set_prefix=False)


def reset_database(reset_db=True, reset_user=True, reset_text=True, reset_annotation=True):
    load()

    if reset_db:
        with MyTask("[Reset DB]"):
            from django.core.management import execute_from_command_line
            if os.path.exists("db.sqlite3"):
                os.remove("db.sqlite3")
            execute_from_command_line(['manage.py', 'makemigrations'])
            execute_from_command_line(['manage.py', 'migrate'])

    from django.contrib.auth.models import User
    if reset_user:
        with MyTask("[Reset User]"):
            User.objects.all().delete()
            User.objects.create_superuser(username="chrisjihee", password="jiheeryu", first_name="Jihee", last_name="Ryu", email="chrisjihee@etri.re.kr")
            User.objects.create_user(username="etri", password="etri.re.kr")
            User.objects.create_user(username="knue", password="knue.ac.kr")
            User.objects.create_user(username="42maru", password="42maru.com")
            print(" User:\n  {}".format(User.objects.all()))

    from ZA.models import Text
    if reset_text:
        with MyTask("[Reset Text]"):
            Text.objects.all().delete()
            num = 0
            for file in list_files("data/texts", ".json"):
                name = os.path.splitext(os.path.basename(file))[0]
                Text.objects.create(textname=name)
                num += 1
            print(" Text:\n  {} texts".format(len(Text.objects.all())))

    from ZA.models import Task
    if reset_annotation:
        with MyTask("[Reset Task]"):
            Task.objects.all().delete()
            num = 0
            for _, r in read_excel("data/tasks.xlsx").iterrows():
                text = Text.objects.get(textname=r["name"])
                for username in [x for x in [r["annotator1"], r["annotator2"]] if not isnull(x)]:
                    user = User.objects.get(username=username)
                    text.task_set.create(user=user)
                    num += 1
            print(" Task:\n  {} tasks".format(len(Task.objects.all())))


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


def export(username, datadir="data/"):
    from ZA.models import Task
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


if __name__ == "__main__":
    # with MyTask("버전 확인"):
    #     check()

    with MyTask("DB 초기화"):
        reset_database()
