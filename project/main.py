# -*- coding: utf8 -*-

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.db import models
from tuples_app.models import *

for i in open('../all.tuples'):
    name, relation, target = i.decode('utf8').strip('\r\n').split('\t', 2)

    relation = relation.strip()
    # remove ""
    relation = relation.strip(u'"')
    # 【】
    relation = relation.strip(u'\u3010\u3011')
    # remove ： and :
    relation = relation.strip(u'\uff1a:')
    # unicode whitespaces
    relation = relation.strip(u'\u3000\u200D\u200B\uFEFF')
    
    try:
        a = Relation(name=name, relation=relation, target=target)
        a.save()
    except Exception as e:
        print "Fail:", name, relation, target