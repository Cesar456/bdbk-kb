#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

def read_extracted_db():
    cat_page_link_dict = {}
    page_id_to_title_dict = {}
    f = open('categorylinks_7_subcat__id_category.txt')
    for line in f:
        page_id, cat_name = line.rstrip().split(' ', 1)
        if cat_name not in cat_page_link_dict:
            cat_page_link_dict[cat_name] = []

        cat_page_link_dict[cat_name].append(page_id)

    f.close()

    f = open('page_0_isredirect__pageid_nsid_title.txt')
    for line in f:
        if ' \n' in line:
            continue
        page_id, _, page_title = line.rstrip().split(' ', 2)
        page_id_to_title_dict[page_id] = page_title
    f.close()
    return (cat_page_link_dict, page_id_to_title_dict)

cat_dict, page_dict = read_extracted_db()

# Circle reference: 陽明學者->王守仁‎->陽明學->陽明學者‎
def extract_categories(cat_name, cat_seen=[], cat_id=None):
    if cat_name not in cat_dict:
        return []
    else:
        sub_cats = []

    for sub_cat_page_id in cat_dict[cat_name]:
        sub_cat_name = page_dict[sub_cat_page_id]
        sub_cat_page_url = 'http://zh.wikipedia.org/wiki?curid=%s' % sub_cat_page_id

        # print 'Processing %s' % sub_cat_name

        if sub_cat_page_id in cat_seen:
            print 'Circle reference found for %s, %s' % (cat_name, cat_id)
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

    return sub_cats

if __name__ == '__main__':
    cats = extract_categories('頁面分類')
    open('data.json', 'w').write(json.dumps(cats))
    print json.dumps(cats)
