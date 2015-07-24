import datetime
import sys
import time
import zlib

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from bdbk.models import *
from bdbk.page_extractor import extractor


class Command(BaseCommand):
    help = 'I will read baidu baike and produce you the info tuples of its infobox. Be sure '
    'to clear the database first!.'

    def add_arguments(self, parser):
        parser.add_argument('--src', required=True, choices=['stdin', 'page', 'mongodb'], help='HTML page source.')
        parser.add_argument('--page-source', type=str, help='page source(page mode).')
        parser.add_argument('--mongod-host', type=str, help='host of mongo db server.')
        parser.add_argument('--mongod-port', type=int, help='port of mongo db server.')
        parser.add_argument('--mongod-from-to', type=str, help='only process part of the docs in mongodb.')

    def handle_page(self, source):
        page_title, search_term, cat_list, tuples = extractor.extract(source)
        print 'Title:', page_title
        print 'Search Term:', search_term
        print 'Categories:', ','.join(cat_list)

        for tuple in tuples:
            print '(', tuple[0], ',', tuple[1], ')'

    def handle_mongodb(self, mongod_host, mongod_port, mongod_from_to):
        logger = logging.getLogger('bdbk.extractor')
        logger.info('mongodb: %s:%d', mongod_host, mongod_port)

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
                    logger.info('%d processed in %d/sec', processed_count, (processed_count-last_processed)/(time.time()-last_time))
                    last_processed = processed_count
                    last_time = time.time()

                try:
                    NamedEntity.updateFromPage(purl, pcontent, plmodified, True)
                except Exception as e:
                    logger.exception('exception %r: page_url(%s)', e, purl)

        def iterator():
            def convert_date_string(s):
                if ' ' in s:
                    date, time = s.split(' ')
                    year, month, day = date.split('-')
                    hour, minute, second = time.split(':')
                else:
                    year, month, day = date.split('-')
                    hour, minute, second = 0, 0, 0
                return timezone.make_aware(
                    datetime.datetime(
                        int(year), int(month), int(day),
                        int(hour), int(minute), int(second)
                    ))

            if slice_skip == -1:
                for item in data_set.find():
                    yield item['actualurl'], convert_date_string(item['lastmodifytime']), zlib.decomporess(item['content'])
            else:
                for item in data_set.find().skip(slice_skip).limit(slice_limit):
                    yield item['actualurl'], convert_date_string(item['lastmodifytime']), zlib.decompress(item['content'])

        do_extract(iterator)
        client.close()
        logger.info('done')

    def handle(self, *args, **options):
        if options['src'] == 'stdin':
            inputs = []
            while True:
                try:
                    inputs.append(raw_input())
                except EOFError as e:
                    break

            source = '\n'.join(inputs)

            self.handle_page(source)
        elif options['src'] == 'page':
            source = open(options['page_source']).read()
            self.handle_page(source)
        elif options['src'] == 'mongodb':
            if options['mongod_host'] is None:
                raise CommandError('--mongod-host should not be null.')
            if options['mongod_port'] is None:
                raise CommandError('--mongod-port should not be null.')
            self.handle_mongodb(options['mongod_host'], options['mongod_port'], options['mongod_from_to'])
