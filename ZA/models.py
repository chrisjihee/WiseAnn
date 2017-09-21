# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class User(models.Model):
    app = models.CharField(max_length=20, default="ZA")
    level = models.IntegerField(default=1)
    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=20)
    fullname = models.CharField(max_length=20)
    telephone = models.CharField(max_length=20)

    def __unicode__(self):
        return "[%s] %s (%s)" % (self.app, self.fullname, self.username)

    def serialize(self):
        return {"username": self.username,
                "fullname": self.fullname,
                "level": self.level,
                "app": self.app}


class Text(models.Model):
    textname = models.CharField(max_length=20)

    def __unicode__(self):
        return "%s" % (self.textname)

    def serialize(self):
        return {"textname": self.textname}


class Task(models.Model):
    user = models.ForeignKey("User")
    text = models.ForeignKey("Text")
    entities = models.TextField(default="{}")
    relations = models.TextField(default="{}")
    finished = models.BooleanField(default=False)

    def __unicode__(self):
        return "[%s] %s <==> %s" % ("O" if self.finished else "X", self.user.username, self.text.textname)

    def serialize(self):
        return {"user": self.user.serialize(),
                "text": self.text.serialize(),
                "finished": self.finished}
