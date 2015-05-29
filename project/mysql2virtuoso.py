#!/usr/bin/python
# -*- coding: utf8 -*-

import re

from virtuoso import sparql
from project.setup_logging import setup as setup_logging

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

def clear_graph():
    sparql_connection.execute('CLEAR GRAPH <http://baike.baidu.com>')
    return 'graph cleared'

def insert_tuples(triple_fn, logging):
    def process_lines(lines, start_line):
        subjects = []
        predicts = []
        objects = []

        regx = re.compile(r'\{\{link:(.*?)\|(.*?)\}\}')
        baike_url_prefix = 'http://baike.baidu.com'

        for line in lines:
            line = line.rstrip()
            page_id, predict, content = line.split('\t')

            match = re.match(regx, content)
            if match is not None:
                object = sparql.SparQLURI(baike_url_prefix+match.group(1))
            else:
                object = sparql.SparQLLiteral(
                    re.sub(regx,
                        lambda x:'{{link:%s|%s}}' % (baike_url_prefix+x.group(1), x.group(2)),
                        content))

            subjects.append(sparql.SparQLURI('http://baike.baidu.com/view/%s.htm' % page_id))
            predicts.append(sparql.SparQLURI(PREDICT_PREDICT_PREFIX + predict))
            objects.append(object)

        try:
            sparql_connection.batch_insert(subjects, predicts, objects)    
        except Exception as e:
            logging.error('exception at block %d(start line): %r', start_line, e)
        else:
            logging.info('(tuple):processed %d/%d(start line) tuples', len(lines), start_line)

    triple_file = open(triple_fn)
    row_size = 500

    line_number = 0
    start_line = 1
    lines = []

    for i in triple_file:
        lines.append(i)

        line_number += 1
        if line_number % row_size == 0:
            process_lines(lines, start_line)
            lines = []
            start_line = line_number

    if len(lines) > 0:
        process_lines(lines, start_line)

    triple_file.close()

def insert_nes(ne_fn, logging):
    def process_lines(lines, start_line):
        subjects = []
        predicts = []
        objects = []

        for line in lines:
            line = line.rstrip()
            page_id, title, search_term = line.split('\t')

            url = 'http://baike.baidu.com/view/%s.htm' % page_id
            subjects.append(sparql.SparQLURI(url))
            predicts.append(sparql.SparQLURI(PREDICT_SEARCH_TERM))
            objects.append(sparql.SparQLLiteral(search_term))

            subjects.append(sparql.SparQLURI(url))
            predicts.append(sparql.SparQLURI(PREDICT_BAIKE_TITLE))
            objects.append(sparql.SparQLLiteral(title))

        try:
            sparql_connection.batch_insert(subjects, predicts, objects)    
        except Exception as e:
            logging.error('exception at block %d(start line): %r', start_line, e)
        else:
            logging.info('(ne):processed %d/%d(start line) tuples', len(lines), start_line)

    ne_file = open(ne_fn)
    row_size = 250

    line_number = 0
    start_line = 1
    lines = []

    for i in ne_file:
        lines.append(i)

        line_number += 1
        if line_number % row_size == 0:
            process_lines(lines, start_line)
            lines = []
            start_line = line_number

    if len(lines) > 0:
        process_lines(lines, start_line)

    ne_file.close()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Dump all triples from mysql to virtuoso.')
    parser.add_argument('--log', required=True, help='log file name.')
    parser.add_argument('--tuple-file', required=True, help='triple dump from database.')
    parser.add_argument('--ne-file', required=True, help='ne dump from database.')
    args = parser.parse_args()
    log_fn = args.log
    tuple_file = args.tuple_file
    ne_file = args.ne_file

    logging = setup_logging(log_fn)

    if clear:
        clear_graph()
    insert_nes(ne_file, logging)
    insert_tuples(tuple_file, logging)

