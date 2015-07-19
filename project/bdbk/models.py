# -*- coding: utf-8 -*-
import logging
import urllib

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .page_extractor import extractor as page_extractor

# data migration must be performed on every schema update
# version: 10

logger = logging.getLogger(__name__)

class Category(models.Model):
    '''
    Ver: 1

    Database Schema:
    name: name of this category, unique across this table
    '''
    name = models.CharField(max_length=255, db_index=True, unique=True)

    @staticmethod
    def getCategoryByName(name, _cache={}):
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
    Ver: 4

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
    bdbk_url = models.CharField(max_length=1024)
    last_modified = models.DateTimeField(null=True, blank=True)
    categories = models.ManyToManyField('Category')

    @staticmethod
    def updateFromPage(url, content, last_modified):
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

            if 'fromid' not in urlquery and urlquery['fromtitle'] == '@#Protect@#':
                return (False, real_url, None)

            if 'type' in urlquery and\
               (urlquery['type'] == 'syn' or urlquery['type'] == 'search') and\
               'fromtitle' in urlquery:
                return (True, real_url, urlquery['fromtitle'])

            logger.warn('bdbk url: %s, does not match common alias signature, needs investigation', url)
            return (False, real_url, None)


        is_alias, real_url, from_title = isAliasUrl()

        try:
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
    id = models.BigIntegerField(primary_key=True)
    named_entity = models.ForeignKey('NamedEntity', db_index=True)
    verb = models.ForeignKey('Verb', db_index=True)
    content = models.TextField()
