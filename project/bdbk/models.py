from django.db import models

class Verb(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class NamedEntity(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class Relation(models.Model):
    named_entity = models.ForeignKey('NamedEntity', db_index=True)
    verb = models.ForeignKey('Verb', db_index=True)
    content = models.TextField()