# -*- coding: utf-8 -*-
from django.db import models


# data migration must be performed on every schema update
# version: 6

class Verb(models.Model):
    '''
    Ver: 1

    Database Schema:
    name: name of this verb, unique across this table.
    '''
    name = models.CharField(max_length=255, db_index=True, unique=True)

class NamedEntity(models.Model):
    '''
    Ver: 2

    Database Schema:
    name: the name for this named entity, for names that could be mapped to
          many entities, there will be additional text appended to "name",
          e.g. "Java（计算机编程语言）"

    search_term: a "cleaner" name for this entity, by typing this keyword in
          baidu baike, you can always be directed to the page(or subview page)
          of this entity. e.g. "Java"

    bdbk_url: where is this named entity extracted from.

    last_modified: last time when the web page of this entity are modified.

    abstract: brief intro of this entity, possibily it could be forcely cut of
          at the middle of a word.

    '''

    name = models.CharField(max_length=255, db_index=True)
    search_term = models.CharField(max_length=255, db_index=True)
    bdbk_url = models.CharField(max_length=1024)
    last_modified = models.DateTimeField(null=True, blank=True)
    abstract = models.TextField()

class InfoboxTuple(models.Model):
    '''
    Ver: 1

    Database Schema:
    named_entity:

    verb:

    content:
          links in attribute values are encoded as: {{link:<relative_or_abs_url>|text}}
    '''
    named_entity = models.ForeignKey('NamedEntity', db_index=True)
    verb = models.ForeignKey('Verb', db_index=True)
    content = models.TextField()

class NamedEntityRedirect(models.Model):
    '''
    Ver: 1

    Database Schema:
    name: TODO
    linked_name: TODO
    '''

    name = models.CharField(max_length=255, db_index=True)
    linked_name = models.CharField(max_length=255, db_index=True)
