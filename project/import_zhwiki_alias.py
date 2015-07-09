#!/usr/bin/python

from django.core.exceptions import ObjectDoesNotExist

import project.setup_database
from zhwiki.models import NamedEntity, NamedEntityNamedAlias

f = open('../PageMapLine.txt')
named_entity_subjects = {}
alias_dict = {}
for i in f:
    neid, name, realid = i.rstrip().split('\t')
    if realid == neid:
        named_entity_subjects[int(neid)] = name
    else:
        if int(realid) not in alias_dict:
            alias_dict[int(realid)] = []
        alias_dict[int(realid)].append(name)

f.close()

for realid, name_list in alias_dict.items():
    target = named_entity_subjects[realid]
    aliases = name_list

    try:
        main = NamedEntity.objects.get(name=target)
        for alias in aliases:
            q = NamedEntityNamedAlias(real_neid=main.neid, alias=alias)
            q.save()
    except ObjectDoesNotExist as e:
        pass
