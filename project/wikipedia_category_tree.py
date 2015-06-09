#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import MySQLdb

connection = MySQLdb.connect(host='localhost',
                             user='root',
                             passwd='root',
                             db='zh_wiki')

cursor = db.cursor()


def extract_categories(cat_name, cat_seen=[], cat_id=None):
    if cat_id in cat_seen:
        print 'Circle reference found for %s, %d' % (cat_name, cat_id)
        return 1

    cursor.execute("select page.page_title, page.page_id from categorylinks inner join page on page.page_id=categorylinks.cl_from where categorylinks.cl_type='subcat' and page.page_is_redirect=0 and categorylinks.cl_to='%s'" % cat_url)

    for sub_cat_name, sub_cat_page_id in cursor.fetchall():
        sub_cat_page_url = 'http://zh.wikipedia.org/wiki?curid=%d' % sub_cat_page_id
        cat_seen.append(sub_cat_page_id)

        print 'Processing %s' % sub_cat_name

        sub_cats.append({
            'name': sub_cat_name,
            'page_url': sub_cat_page_url,
            'subcats': extract_categories(sub_cat_name, cat_seen, sub_cat_page_id)
        })

    return sub_cats

if __name__ == '__main__':
    cats = extract_categories('頁面分類')
    open('data.json', 'w').write(json.dumps(cats))
    print json.dumps(cats)
