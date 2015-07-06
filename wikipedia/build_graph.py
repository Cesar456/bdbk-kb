#!/usr/bin/python

import json

class CategoryGraph(object):
    def __init__(self, category_fn, category_link_fn):
        self.cat__name_id = {}
        self.cat__id_name = {}
        self.graph_inlink = {}
        self.graph_outlink = {}

        # read all cat names
        for cat in json.loads(open(category_fn).read()):
            name = cat['name']
            pageId = int(cat['pageId'])

            if name in self.cat__name_id:
                print 'Warning: duplicate(name) category: %s,%d' % (name, pageId)
            else:
                self.cat__name_id[name] = pageId

            if pageId in self.cat__id_name:
                print 'Warning: duplicate(id) category: %s,%d' % (name, pageId)
            else:
                self.cat__id_name[pageId] = name

        print 'Category names imported.'

        # read inlink graph
        for inlink in json.loads(open(category_link_fn).read()):
            pageId = int(inlink['id'])
            inLink = int(inlink['inLinks'])

            if pageId not in self.cat__id_name or inLink not in self.cat__id_name:
                print 'Warning: inlink id (%d->%d) could not be deferenced' % (inLink, pageId)
            else:
                if pageId not in self.graph_inlink:
                    self.graph_inlink[pageId] = []

                self.graph_inlink[pageId].append(inLink)

        print 'Inlink graph imported.'

        # build outlink graph
        print 'Building outlink graph...',
        total_size = len(self.graph_inlink)
        counter = 0
        link_counter = 0
        for pageId in self.graph_inlink:
            inLinks = self.graph_inlink[pageId]

            for inLink in inLinks:
                if inLink not in self.graph_outlink:
                    self.graph_outlink[inLink] = []

                self.graph_outlink[inLink].append(pageId)
                link_counter += 1

            counter += 1
            if counter % 30000 == 0:
                print ',%%%d' % (counter*100/total_size),

        print 'Done'
        print '%d categories, %d links' % (len(self.cat__id_name), link_counter)

    def outlink_name(self, cat_title):
        pageId = self.cat__name_id[cat_title]
        links = self.graph_outlink.get(pageId, None)

        if links:
            for link in links:
                yield self.cat__id_name[link]

    def outlink(self, cat_id):
        links = self.graph_outlink.get(cat_id, None)

        if links:
            for link in links:
                yield link

    def inlink_name(self, cat_title):
        pageId = self.cat__name_id[cat_title]
        links = self.graph_inlink.get(pageId, None)

        if links:
            for link in links:
                yield self.cat__id_name[link]

    def inlink(self, cat_id):
        links = self.graph_inlink.get(cat_id, None)

        if links:
            for link in links:
                yield link

graph = CategoryGraph('Category.json', 'category_inlinks.json')
import code
code.interact(local=locals())
