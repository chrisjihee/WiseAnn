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
                return x.objects.get(username=username, password=password)
            else:
                return x.objects.get(username=username)
        except x.DoesNotExist:
            pass
    return None


def need_auth(call):
    def try_auth(request, *args, **kwargs):
        global user
        if "HTTP_AUTHORIZATION" in request.META:
            (u, p) = decodestring(request.META["HTTP_AUTHORIZATION"]).split(":")
            user = get_user(u, p)
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
