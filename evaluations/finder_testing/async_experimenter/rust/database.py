#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 huang <huang@huang-Precision-WorkStation-T3500>
#
# Distributed under terms of the MIT license.

"""
This is for lint checks
"""

from peewee import *
import datetime
import os

db = MySQLDatabase("rust_crates", host="localhost", user="root", password="zqy1dimmbnRAAT3L")

class BaseModel(Model):
    class Meta:
        database = db

class Crate(BaseModel):
    name = CharField()
    version = CharField()
    cratefile = CharField()
    srcdir = CharField(unique=True)
    updated_time = DateTimeField(default=datetime.datetime.now)

class MutLintChecker(BaseModel):
    crate = ForeignKeyField(Crate, related_name="crates")
    total_functions = IntegerField()
    mutrtn_functions = IntegerField()
    imut2mut_functions = IntegerField()
    pass_build = BooleanField(default=True)
    build_time = DateTimeField(default=datetime.datetime.now)


def init_db():
    if db.get_tables() != []:
        db.drop_tables([Crate,MutLintChecker])
    db.create_tables([Crate, MutLintChecker])
    print("Database Initializing Finished!")


def test():
    print(db.get_tables())
    init_db()
    new_crate = Crate(name="Hello",version="0.1.10",srcdir="/home/huang") #add
    new_crate.save()

if __name__ == "__main__":
    test()
    #db.create_tables([MutLintChecker])
