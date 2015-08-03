# -*- coding: utf-8 -*-
import logging
import urllib

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import fields

from .page_extractor import extractor as page_extractor


# data migration must be performed on every schema update
# version: 13
DBVersion = '0.13'

class BigAutoField(models.fields.AutoField):
    def db_type(self, connection):
        if 'mysql' in connection.__class__.__module__:
            return 'bigint AUTO_INCREMENT'
        elif 'postgresql' in connection.__class__.__module__:
            return 'bigserial'
        return super(BigAutoField, self).db_type(connection)

class BigForeignKey(models.ForeignKey):
    def db_type(self, connection):
        """ Adds support for foreign keys to big integers as primary keys.
        """
        rel_field = self.rel.get_related_field()
        if (isinstance(rel_field, BigAutoField) or
                (not connection.features.related_fields_match_type and
                isinstance(rel_field, (BigIntegerField, )))):
            return models.BigIntegerField().db_type(connection=connection)
        return super(BigForeignKey, self).db_type(connection)

class Category(models.Model):
    '''
    Ver: 1

    Database Schema:
    name: name of this category, unique across this table
    '''
    name = models.CharField(max_length=255, db_index=True, unique=True)

    @staticmethod
    def getCategoryByName(name, _cache={}):
        logger = logging.getLogger('bdbk.extractor')

        if name in _cache:
            logger.debug('Category cache hit: %s', name)
            return _cache[name]
        else:
            (cat_object, created) = Category.objects.get_or_create(name=name)
            logger.debug('Category cache miss: %s, create: %r', name, created)
            _cache[name] = cat_object
            return cat_object

class Verb(models.Model):
    '''
    Ver: 1

    Database Schema:
    name: name of this verb, unique across this table.
    '''
    name = models.CharField(max_length=255, db_index=True, unique=True)

    @staticmethod
    def getVerbByName(name, _cache = {}):
        logger = logging.getLogger('bdbk.extractor')

        if name in _cache:
            logger.debug('Verb cache hit: %s', name)
            return _cache[name]
        else:
            (verb_object, created) = Verb.objects.get_or_create(name=name)
            logger.debug('Verb cache miss: %s, create: %r', name, created)
            _cache[name] = verb_object
            return verb_object

class NamedEntityAlias(models.Model):
    '''
    Ver: 2

    Database Schema:
    link_to: where does this alias link to.

    link_from_name: the name of this alias.

    '''
    link_to = models.ForeignKey('NamedEntity')
    link_from = models.CharField(max_length=255, db_index=True, unique=True)

class NamedEntity(models.Model):
    '''
    Ver: 5

    Database Schema:
    name: the name for this named entity, for names that could be mapped to
          many entities, there will be additional text appended to "name",
          e.g. "Java（计算机编程语言）"

    search_term: a "cleaner" name for this entity, by typing this keyword in
          baidu baike, you can always be directed to the page(or subview page)
          of this entity. e.g. "Java"

    bdbk_url: where is this named entity extracted from.

    last_modified: last time when the web page of this entity are modified.

    abstract: SHOULD BE REMOVED. brief intro of this entity, possibily it
          could be forcely cut off at the middle of a word.

    '''

    name = models.CharField(max_length=255, db_index=True)
    search_term = models.CharField(max_length=255, db_index=True)
    bdbk_url = models.CharField(max_length=255, db_index=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    categories = models.ManyToManyField('Category')

    @staticmethod
    def updateFromPage(url, content, last_modified, sure_new=False):
        logger = logging.getLogger('bdbk.extractor')

        def isAliasUrl():
            '''
            Returns (is_alias, fromtitle, fromid)
            '''
            if '?' not in url:
                return (False, url, None)

            real_url, parms = url.encode('utf8').split('?', 1)
            urlquery = {}
            for i in parms.split('&'):
                key, value = i.split('=')
                urlquery[key] = urllib.unquote(value).decode('utf8')

            if 'fromtitle' in urlquery and 'fromid' in urlquery:
                return (True, real_url, urlquery['fromtitle'])

            if 'fromid' not in urlquery and urlquery.get('fromtitle', '') == '@#Protect@#':
                return (False, real_url, None)

            if 'type' in urlquery and\
               (urlquery['type'] == 'syn' or urlquery['type'] == 'search') and\
               'fromtitle' in urlquery:
                return (True, real_url, urlquery['fromtitle'])

            logger.warn('bdbk url: %s, does not match common alias signature, needs investigation', url)
            return (False, real_url, None)


        is_alias, real_url, from_title = isAliasUrl()

        try:
            if sure_new:
                raise ObjectDoesNotExist()

            ne_object = NamedEntity.objects.get(bdbk_url=real_url)
            if ne_object.last_modified > last_modified:
                should_edit = False
            else:
                should_edit = True

            logger.debug('updateFromPage(%s): db record updated, should_edit=%r', url, should_edit)

            # we have this object
        except ObjectDoesNotExist as e:
            ne_object = NamedEntity()
            should_edit = True
            logger.debug('updateFromPage(%s): db record created', url)

        if should_edit:
            page_title, search_term, cats, infoboxtuples = page_extractor.extract(content)
            ne_object.name = page_title
            ne_object.search_term = search_term
            ne_object.last_modified = last_modified
            ne_object.bdbk_url = real_url
            ne_object.save()

            if not sure_new:
                ne_object.categories.clear()

            for cat in cats:
                ne_object.categories.add(Category.getCategoryByName(cat))

            # currently we remove all old infoboxtuples, this is not good
            ne_object.infoboxtuple_set.all().delete()

            for verb, content in infoboxtuples:
                ibt = InfoboxTuple(named_entity=ne_object,
                                   verb=Verb.getVerbByName(verb),
                                   content=content)
                ibt.save()

            logger.debug('updateFromPage(%s): %d infobox tuples inserted', url, len(infoboxtuples))

        # update aliases
        if from_title:
            (alias, created) = NamedEntityAlias.objects.get_or_create(link_from=from_title, link_to=ne_object)
            logger.debug('updateFromPage(%s): create alias as %s: %r', url, from_title, created)

class InfoboxTuple(models.Model):
    '''
    Ver: 1

    Database Schema:
    named_entity:

    verb:

    content:
          links in attribute values are encoded as: {{link:<relative_or_abs_url>|text}}
    '''
    id = BigAutoField(primary_key=True)
    named_entity = models.ForeignKey('NamedEntity', db_index=True)
    verb = models.ForeignKey('Verb', db_index=True)
    content = models.TextField()

    def delete(self, *args, **kwargs):
        # delete all links of this tuple to make sure there are no
        # dead links in db
        self.infoboxtupelink_set.delete()
        super(InfoboxTuple, self).delete(*args, **kwargs)

class InfoboxTupleLink(models.Model):
    '''
    Ver: 2

    Database Schema:

    id:
    start:
    end:
    infoboxtuple:
    linkcontent: {{alias_id:\d+}}|{{ne_id:\d+}}
    '''
    id = BigAutoField(primary_key=True)
    start = models.IntegerField()
    end = models.IntegerField()
    infoboxtuple = BigForeignKey('InfoboxTuple', db_index=True)
    linkcontent = models.CharField(max_length=255)
