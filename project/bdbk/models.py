from django.db import models

class Verb(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)

class NamedEntity(models.Model):
    '''
    page_id is the baidu baike page id.
    '''

    name = models.CharField(max_length=255, db_index=True)
    search_term = models.CharField(max_length=255, db_index=True)
    abstract = models.TextField()
    page_id = models.IntegerField()

class InfoboxTuple(models.Model):
    named_entity = models.ForeignKey('NamedEntity', db_index=True)
    verb = models.ForeignKey('Verb', db_index=True)
    content = models.TextField()

class NamedEntityRedirect(models.Model):
    '''
    page_id is the baidu baike page id.
    named_entities is a list of named_entities separated by comma.
    '''

    page_id = models.IntegerField()
    name = models.CharField(max_length=255, db_index=True)
    linked_name = models.CharField(max_length=255, db_index=True)