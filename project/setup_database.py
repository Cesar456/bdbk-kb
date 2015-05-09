# -*- coding: utf8 -*-

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.db import models
from bdbk.models import Verb as BaiduVerb
from bdbk.models import NamedEntity as BaiduNamedEntity
from bdbk.models import InfoboxTuple as BaiduInfoboxTuple
from bdbk.models import NamedEntityRedirect as BaiduNamedEntityRedirect

from zhwiki.models import Verb as ZhWikiVerb
from zhwiki.models import NamedEntity as ZhWikiNamedEntity
from zhwiki.models import Relation as ZhWikiRelation

import django
django.setup()