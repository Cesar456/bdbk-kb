from django.db import models
import re

ne_regx = re.compile(r'^(.*?)_\(.*?\)$')

# every time version number is updated, 
# data migration must be performed
# version: 2

class Verb(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class NamedEntity(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    search_term = models.CharField(max_length=255, db_index=True)
    neid = models.IntegerField()

    def extract_search_term(self):
        mch = re.match(ne_regx, self.name)
        if mch:
            self.search_term = mch.group(1)
        else:
            self.search_term = self.name

class Relation(models.Model):
    named_entity = models.ForeignKey('NamedEntity', db_index=True)
    verb = models.ForeignKey('Verb', db_index=True)
    # if not content_neid, then content != ''
    content_neid = models.IntegerField(db_index=True, blank=True, null=True)
    content = models.TextField(default='')

class NamedEntityAlias(models.Model):
    # NamedEntity.neid
    real_neid = models.IntegerField()
    alias_neid = models.IntegerField()