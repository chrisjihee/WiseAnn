# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base64 import decodestring

from django.http import JsonResponse
from django.views.decorators.cache import never_cache

import ZA.models

user = None


def get_user(username, password=None):
    global user
    for x in [ZA.models.User]:
        try:
            if password is not None:
                user = x.objects.get(username=username, password=password)
                return user
            else:
                user = x.objects.get(username=username)
                return user
        except x.DoesNotExist:
            pass
    return None


def auth_user(request):
    global user
    if "HTTP_AUTHORIZATION" in request.META and len(request.META["HTTP_AUTHORIZATION"]) > 0:
        authcode = decodestring(request.META["HTTP_AUTHORIZATION"])
        parts = authcode.split(":", 2)
        if len(parts) == 2:
            (u, p) = authcode.split(":", 2)
            user = get_user(u, p)
            return user
    return user


def need_auth(call):
    def try_auth(request, *args, **kwargs):
        print("-----try_auth-----")
        global user
        user = None
        auth_user(request)
        if user is not None:
            return call(request, *args, **kwargs)
        return JsonResponse({"status": 401, "msg": "Unauthorized"}, status=401)

    return try_auth


@need_auth
@never_cache
def login(request):
    if user is not None:
        return JsonResponse({"status": 200, "msg": "OK", "user": user.serialize()}, status=200)
    else:
        return JsonResponse({"status": 401, "msg": "Unauthorized"}, status=401)
