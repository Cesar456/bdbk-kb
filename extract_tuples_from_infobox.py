#!/usr/bin/python
# This script reads baidu baike data, and parses its infobox, produces
# tuples of the name entities

import scrapy
import re
import os
import gzip
import sys

import argparse

parser = argparse.ArgumentParser(
    description='I will read baidu baike and produce you the info tuples of its infobox.')
parser.add_argument('--index', required=True, help='index file of baike database.')
parser.add_argument('--page-ids', help='only extract data from pages specified in this list file.')
parser.add_argument('--output', required=True, help='output file name.')
parser.add_argument('--log', required=True, help='log file name.')

args = parser.parse_args()
index_file = args.index
dest_file = args.output
log_fn = args.log

page_ids = None
if args.page_ids:
    f = open(args.page_ids)
    page_ids = []
    for line in f:
        page_ids.append(int(line))

    f.close()

from setup_logging import setup as setup_log
logging = setup_log(log_fn)

logging.info('Source folder: %s', index_file)
logging.info('Output: %s', dest_file)
logging.info('Extracting %d special pages', len(page_ids))

meta_data = open(dest_file, 'wa')

def extract_information(page_id, content):
    # scrapy doc says it will detect encoding, but we should really
    # be careful at that
    page = scrapy.http.TextResponse(
        "file:///", 
        headers={}, 
        status=200, 
        body=content)

    # page title
    #page_title = page.xpath("//*[contains(@class,'lemmaTitleBox')]")
    page_title = page.xpath("//*[starts-with(@class, 'lemmaTitle')][last()]//text()")
    page_title = page_title.extract()
    if len(page_title) == 1:
        page_title = page_title[0]
    elif len(page_title) != 0:
        page_title = page_title[0]
    else:
        # are we at disambiguity page?
        if len(page.xpath("//*[contains(@id, 'lemma-list')]")) > 0:
            return

        # 404 page...
        if len(page.xpath("//*[@class='sorryBubble']")) > 0:
            return

        logging.warning('Unable to extract title: page_id(%d)', page_id)
        return

    tuples = []

    page_biitems = page.xpath("//*[@class='biItem']")
    for i in page_biitems:
        page_bititle = i.xpath(".//*[@class='biTitle']//text()").extract()
        bititle = re.sub(r'[\xa0\s]', '', page_bititle[0])

        # if we have a <br>, then multiple bicontents should be produced
        page_bicontents = i.xpath(".//*[@class='biContent']//text()").extract()
        target = ''

        #in_href=False
        for bicontent in page_bicontents:
            if '\n' in bicontent:
                target += re.sub(r'[\xa0\s\n]', '', bicontent)
                if target:
                    tuples.append((page_title, bititle, target))
                target = ''
            else:
                target += bicontent.strip()

        tuples.append((page_title, bititle, target))

    if len(tuples):
        logging.info('%d meta data: page_id(%d)', len(tuples), page_id)
    else:
        logging.info('no meta data: page_id(%d)', page_id)

    for i in tuples:
        meta_data.write('\t'.join(i).encode('utf8'))
        meta_data.write('\n')
    return tuples

f = open(index_file)
gzfile_suffix = index_file[:index_file.rfind('.')]
gzip_file = None
gzip_file_id = -1
for line in f:
    line = re.sub(r'[\r\n]', '', line).decode('utf8')
    if not line.strip():
        break

    page_id, title, fid, offset, size = line.split('\t')
    page_id = int(page_id)
    if page_ids and page_id not in page_ids:
        continue
        
    fid = int(fid)
    offset = int(offset)
    size = int(size)

    if gzip_file_id != fid:
        gzip_file_id = fid
        if gzip_file:
            gzip_file.close()
        gzip_file = gzip.open('%s.%.3d.gz' % (gzfile_suffix, gzip_file_id))

    gzip_file.seek(offset)
    content = gzip_file.read(size)

    try:
        extract_information(page_id, content)
    except Exception as e:
        logging.warning('exception %r: page_id(%d)', e, page_id)

if gzip_file:
    gzip_file.close()

f.close()
meta_data.close()
