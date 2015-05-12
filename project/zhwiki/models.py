from django.db import models


# every time version number is updated, 
# data migration must be performed
# version: 1

class Verb(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class NamedEntity(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    neid = models.IntegerField()

class Relation(models.Model):
    named_entity = models.ForeignKey('NamedEntity', db_index=True)
    verb = models.ForeignKey('Verb', db_index=True)
    # if not content_neid, then content != ''
    content_neid = models.IntegerField(db_index=True, blank=True, null=True)
    content = models.TextField(default='')
