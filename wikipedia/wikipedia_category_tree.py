#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
import urllib
from cgi import parse_qs
from wsgiref.simple_server import make_server


PWD = '/Users/huohaoyan/DO_NOT_BACKUP/'

def read_extracted_db():
    cat_page_link_dict = {}
    page_id_to_title_dict = {}
    f = open(PWD+'categorylinks_7_subcat__id_category.txt')
    for line in f:
        page_id, cat_name = line.rstrip().split(' ', 1)
        if cat_name not in cat_page_link_dict:
            cat_page_link_dict[cat_name] = []

        cat_page_link_dict[cat_name].append(page_id)

    f.close()

    f = open(PWD+'page_0_isredirect__pageid_nsid_title.txt')
    for line in f:
        if ' \n' in line:
            continue
        page_id, _, page_title = line.rstrip().split(' ', 2)
        page_id_to_title_dict[page_id] = page_title
    f.close()
    return (cat_page_link_dict, page_id_to_title_dict)

# Circle reference: 陽明學者->王守仁‎->陽明學->陽明學者‎
def extract_categories(cat_name, cat_seen=[], cat_id=None):
    if cat_name not in cat_dict:
        return []
    else:
        sub_cats = []

    for sub_cat_page_id in cat_dict[cat_name]:
        try:
            sub_cat_name = page_dict[sub_cat_page_id]
        except KeyError as e:
            sub_cat_name = 'WARNING:404INPAGE'

        sub_cat_page_url = 'http://zh.wikipedia.org/wiki?curid=%s' % sub_cat_page_id

        # print 'Processing %s' % sub_cat_name

        if sub_cat_page_id in cat_seen:
            # print 'Circle reference found for %s, %s' % (cat_name, cat_id)
            sub_cats.append({
                'name': sub_cat_name,
                'page_url': sub_cat_page_url,
                'subcats': True
            })
        else:
            cat_seen.append(sub_cat_page_id)
            sub_cats.append({
                'name': sub_cat_name,
                'page_url': sub_cat_page_url,
                'subcats': extract_categories(sub_cat_name, cat_seen, sub_cat_page_id)
            })

        sys.stdout.write('.')

    sys.stdout.write('\n')
    return sub_cats

class TreeServer(object):
    def __init__(self):
        self.cat_dict, self.page_dict = read_extracted_db()

    def __call__(self, environ, start_response):
        folder = parse_qs(environ['QUERY_STRING']).get('title', None)[0]

        cat_title = urllib.unquote(folder)
        sub_cats = []
        for sub_cat_page_id in self.cat_dict[cat_title]:
            try:
                sub_cats.append({
                    'name': self.page_dict[sub_cat_page_id]
                })
            except KeyError as e:
                sub_cats.append({
                    'name': 'INVALID' + str(sub_cat_page_id)
                })


        start_response('200 OK', [])
        return [json.dumps(sub_cats)]

if __name__ == '__main__':
    httpd = make_server('localhost', 1337, TreeServer())
    print "Serving on port 1337..."
    httpd.serve_forever()

    # cats = extract_categories('頁面分類')
    # open('data.json', 'w').write(json.dumps(cats))
    # print json.dumps(cats)
