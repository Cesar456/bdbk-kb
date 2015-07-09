# -*- coding: utf8 -*-

import os

import django
from django.db import models

from bdbk.models import InfoboxTuple as BaiduInfoboxTuple
from bdbk.models import NamedEntity as BaiduNamedEntity
from bdbk.models import NamedEntityRedirect as BaiduNamedEntityRedirect
from bdbk.models import Verb as BaiduVerb
from zhwiki.models import NamedEntity as ZhWikiNamedEntity
from zhwiki.models import Relation as ZhWikiRelation
from zhwiki.models import Verb as ZhWikiVerb

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")



django.setup()
