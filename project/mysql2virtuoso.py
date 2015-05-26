#!/usr/bin/python
# -*- coding: utf8 -*-

import re

from django.core.paginator import Paginator
from django.db import connection

import project.setup_database
from bdbk.models import NamedEntity
from virtuoso import sparql

PREDICT_SEARCH_TERM = 'http://baike.baidu.com/graph#search_term'
PREDICT_BAIKE_TITLE = 'http://baike.baidu.com/graph#baike_title'
PREDICT_PREDICT_PREFIX = 'http://baike.baidu.com/predicts#'

sparql_connection = sparql.SparQL('http://localhost:8890/sparql/',
    'http://baike.baidu.com/')

def delete_all_tuples():
    count = 0
    for s, p, o in sparql_connection.query():
        sparql_connection.delete(s, p, o)
        print 'deleted', s, p, o
        count +=1
    print 'total:', count

def insert_tuples():
    cursor = connection.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM bdbk_infoboxtuple
        ''')
    total_count = cursor.fetchall()[0][0]

    query = '''
        SELECT bdbk_infoboxtuple.content, 
            bdbk_namedentity.page_id, 
            bdbk_verb.name 
        FROM bdbk_infoboxtuple 
        INNER JOIN bdbk_namedentity 
            ON bdbk_infoboxtuple.named_entity_id = bdbk_namedentity.id 
        INNER JOIN bdbk_verb 
            on bdbk_infoboxtuple.verb_id = bdbk_verb.id 
        LIMIT %d,%d
        '''

    row_size = 1000
    regx = re.compile(r'\{\{link:(.*?)\|(.*?)\}\}')
    baike_url_prefix = 'http://baike.baidu.com'

    for offset in range(0, total_count, row_size):
        cursor.execute(query % (offset, row_size))
        rows = cursor.fetchall()
        for row in rows:
            content, page_id, predict = row
            match = re.match(regx, content)
            if match is not None:
                object = sparql.SparQLURI(baike_url_prefix+match.group(1))
            else:
                object = sparql.SparQLLiteral(
                    re.sub(regx,
                        lambda x:'{{link:%s|%s}}' % (baike_url_prefix+x.group(1), x.group(2)),
                        content))

            sparql_connection.insert(
                sparql.SparQLURI('http://baike.baidu.com/view/%d.htm' % page_id),
                sparql.SparQLURI(PREDICT_PREDICT_PREFIX + predict),
                sparql.SparQLLiteral(object))

        print 'processed', len(rows), 'tuples'

def insert_nes():
    paginator = Paginator(NamedEntity.objects.all(), 1000)
    for page in range(1, paginator.num_pages + 1):
        for i in paginator.page(page).object_list:
            search_term = i.search_term
            title = i.name
            page_id = i.page_id

            url = 'http://baike.baidu.com/view/%d.htm' % page_id
            sparql_connection.insert(
                sparql.SparQLURI(url),
                sparql.SparQLURI(PREDICT_SEARCH_TERM),
                sparql.SparQLLiteral(search_term))
            sparql_connection.insert(
                sparql.SparQLURI(url),
                sparql.SparQLURI(PREDICT_BAIKE_TITLE),
                sparql.SparQLLiteral(title))

        print 'inserted', len(paginator.page(page).object_list), 'pages'

insert_nes()
insert_tuples()
delete_all_tuples()
