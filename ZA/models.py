# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Text(models.Model):
    textname = models.CharField(max_length=20)

    def __str__(self):
        return "%s" % self.textname

    def serialize(self):
        return {"textname": self.textname}


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    entities = models.TextField(default="{}")
    relations = models.TextField(default="{}")
    finished = models.BooleanField(default=False)

    def __str__(self):
        return "[%s] %s <==> %s" % ("O" if self.finished else "X", self.user.username, self.text.textname)

    def serialize(self):
        return {"user": self.user.username,
                "text": self.text.textname,
                "finished": self.finished}
