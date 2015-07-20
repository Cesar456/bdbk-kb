#!/usr/bin/python
# -*- coding: utf-8 -*-
# This script reads baidu baike data, and parses its infobox, produces
# tuples of the name entities

import argparse
import datetime
import logging
import sys
import time

import project.setup_database
from bdbk.models import *
from bdbk.page_extractor import extractor
from dbutils.baidu_database import BaiduDatabase

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='I will read baidu baike and produce you the info tuples of its infobox.')
    parser.add_argument('--src', required=True, choices=['stdin', 'page', 'archive', 'mongodb'], help='HTML page source.')
    parser.add_argument('--page-source', type=str, help='page source(page mode).')
    parser.add_argument('--archive-dir', type=str, help='archive dir(archive mode).')
    parser.add_argument('--archive-name', type=str, help='name of the archive(archive mode).')
    parser.add_argument('--mongod-host', type=str, help='host of mongo db server.')
    parser.add_argument('--mongod-port', type=int, help='port of mongo db server.')
    parser.add_argument('--mongod-from-to', type=str, help='only process part of the docs in mongodb.')
    parser.add_argument('--mongod-list', type=str, help='a list file of _id to extract.')
    parser.add_argument('--log', help='log file name.')

    args = parser.parse_args()

    def do_extract(iterator):
        '''
        iterator: every item should be like: (url, last_modified, content)
        '''
        verb_dict = {}

        processed_count = 0
        last_time = time.time()
        last_processed = 0

        for purl, plmodified, pcontent in iterator():
            processed_count += 1
            if processed_count % 100 == 0:
                logging.info('%d processed in %d/sec', processed_count, (processed_count-last_processed)/(time.time()-last_time))
                last_processed = processed_count
                last_time = time.time()

            try:
                NamedEntity.updateFromPage(purl, pcontent, plmodified)
            except Exception as e:
                logging.warning('exception %r: page_url(%s)', e, purl)


    def do_data_archive(archive_dir, archive_name):
        db = BaiduDatabase(archive_dir, archive_name)

        def iterator():
            for pid, ptitle, pcontent in db.all_pages():
                yield 'http://baike.baidu.com/view/%d.htm' % pid, \
                    datetime.datetime(1970, 1, 1, 0, 0, 0), \
                    pcontent

        do_extract(iterator)
        db.close()

    def do_mongodb(mongod_host, mongod_port, mongod_from_to, mongod_list):
        import pymongo
        client = pymongo.MongoClient(mongod_host, mongod_port)
        data_set = client.baidu.data

        if mongod_from_to:
            slice_skip, slice_limit = mongod_from_to.split('-')
            slice_skip = int(slice_skip)
            slice_limit = int(slice_limit) - slice_skip
        else:
            slice_skip = -1
            slice_limit = -1

        def iterator():
            def convert_date_string(s):
                year, month, day = s.split('-')
                return datetime.datetime(int(year), int(month), int(day))

            if not mongod_list:
                if slice_skip == -1:
                    for item in data_set.find():
                        yield item['actualurl'], convert_date_string(item['lastmodifytime']), item['content']
                else:
                    for item in data_set.find().skip(slice_skip).limit(slice_limit):
                        yield item['actualurl'], convert_date_string(item['lastmodifytime']), item['content']
            else:
                listfile = open(mongod_list)
                for _id in listfile:
                    item = data_set.find_one({'_id': _id})
                    yield item['actualurl'], convert_date_string(item['lastmodifytime']), item['content']

        do_extract(iterator)
        client.close()

    src = args.src

    if src == 'page':
        if not args.page_source:
            logging.error('page mode specified, but no page source found in console arguments.')
            sys.exit(1)

    if src == 'archive':
        archive_dir = args.archive_dir
        archive_name = args.archive_name
        if not archive_dir or not archive_name:
            logging.error('archive mode specified, but no archive found in console arguments.')
            sys.exit(1)

    if src == 'mongodb':
        mongod_host = args.mongod_host
        mongod_port = args.mongod_port
        mongod_list = args.mongod_list
        mongod_from_to = args.mongod_from_to

        if not mongod_host or not mongod_port:
            logging.error('mongodb mode specified, but no host/port pair given.')
            sys.exit(1)

    if args.log:
        from project.setup_logging import setup as setup_logger
        logging = setup_logger(args.log)

    logging.info('Source: %s', src)

    if src == 'stdin' or src == 'page':
        if src == 'stdin':
            inputs = []
            while True:
                try:
                    inputs.append(raw_input())
                except EOFError as e:
                    break

            source = '\n'.join(inputs)
        else:
            source = open(args.page_source).read()

        page_title, search_term, cat_list, tuples = extractor.extract(source)
        print 'Title:', page_title
        print 'Search Term:', search_term
        print 'Categories:', ','.join(cat_list)

        for tuple in tuples:
            print '(', tuple[0], ',', tuple[1], ')'

    elif src == 'archive':
        logging.info('Archive mode: %s in %s', archive_name, archive_dir)
        do_data_archive(archive_dir, archive_name)
    elif src == 'mongodb':
        logging.info('Mongo DB mode: %s:%d', mongod_host, mongod_port)
        do_mongodb(mongod_host, mongod_port, mongod_from_to, mongod_list)
