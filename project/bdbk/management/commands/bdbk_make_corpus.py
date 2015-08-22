import random
import re
import zlib
from StringIO import StringIO

import jieba
import pymongo
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from lxml import etree


class Command(BaseCommand):
    help = 'Make corpus for word2vec from bdbk text database.'

    def add_arguments(self, parser):
        parser.add_argument('--corpus-output', required=True, type=str, help='output corpus file.')
        parser.add_argument('--nb-words', required=True, type=int, help='estimated number of words of output corpus.')
        parser.add_argument('--batch-size', type=int, default=10, help='document access batch size (to improve performance).')

    def handle(self, *args, **options):
        corpus_output = options['corpus_output']
        batch_size = options['batch_size']
        nb_words = options['nb_words']
        mongodb_settings = settings.BDBK_SETTINGS['page_source_mongodb']
        mongod_host = mongodb_settings['host']
        mongod_port = mongodb_settings['port']

        output_corpus_f = open(corpus_output, 'w')

        db = pymongo.MongoClient(mongod_host, mongod_port)
        doc_count = db.baidu.data.find().count()
        fetched_docs = {}

        nb_words_fetched = 0

        def _fetch_doc():
            doc_start = random.randint(0, doc_count-1)
            doc_size = min(doc_count-doc_start, batch_size)
            docs = list(db.baidu.data.find().skip(doc_start).limit(doc_size))

            result = []
            for i in range(len(docs)):
                doc_id = doc_start + i
                if doc_id not in fetched_docs:
                    print doc_id
                    fetched_docs[doc_id] = 1
                    result.append(docs[i])

            return result

        def _process_doc(mongo_obj):
            try:
                data = zlib.decompress(mongo_obj['content'])
            except Exception as e:
                data = mongo_obj['content']

            root = etree.parse(StringIO(data), etree.HTMLParser(encoding='utf8'))

            processed_words = 0
            for para in root.xpath('//div[@class="para"]'):
                words = list(jieba.cut(re.sub(r'\s+', ' ', para.xpath('string(.)')), cut_all=False))
                processed_words += len(words)
                output_corpus_f.write(' '.join(words).encode('utf8'))
                output_corpus_f.write(' ')

            return processed_words

        while nb_words_fetched < nb_words:
            docs = _fetch_doc()
            nb_words_fetched += len(docs)
            for doc in docs:
                nb_words_fetched += _process_doc(doc)

        output_corpus_f.close()
