#!/usr/bin/python
# -*- coding:utf-8 -*-
import json

class CategoryGraph(object):
    def __init__(self, category_fn, category_link_fn, hiddencat_fn):
        self.cat__name_id = {}
        self.cat__id_name = {}
        self.graph_inlink = {}
        self.graph_outlink = {}
        self.stop_cats = []

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

        # read hidden cats(stop cats)
        for hidden_cats in json.loads(open(hiddencat_fn).read()):
            self.stop_cats.append(hidden_cats['title'])

        print 'Stop category(hidden category) list imported.'

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
        print '%d categories(%d hidden), %d links' % (len(self.cat__id_name), len(self.stop_cats), link_counter)

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

# Category.json: list of dict: {'id':'...', 'pageId':'...', 'name': '...'}
# category_inlinks.json: list of dict: {'id':'...', 'inLinks':'...'}
# hiddencats_without_id.json: list of dict: {'title':'...', 'url':'...(not used)'}
graph = CategoryGraph('Category.json', 'category_inlinks.json', 'hiddencats_without_id.json')

def browser(graph, current=None):
    def select(lst, help):
        for i in range(0, len(lst)):
            outlink = lst[i]
            print '[%d]: %s(%d)' % (i, graph.cat__id_name[outlink], outlink)

        print '\n' + help

        s = raw_input()
        if not s:
            return -1
        else:
            return int(s)

    current = 254517 if not current else current
    print 'Welcome'
    while True:
        outlinks = graph.graph_outlink[current]
        print 'Current category: %s(%d), with %d children' % (graph.cat__id_name[current], current, len(outlinks))
        cmd = select(outlinks, '%d-%d to select, 0 to go up' % (0, len(outlinks)-1))

        oldcurrent = current
        if cmd >= 0 and cmd < len(outlinks):
            current = outlinks[cmd]
            if current not in graph.graph_outlink:
                print '%s(%d) has no child\n' % (graph.cat__id_name[current], current)
                current = oldcurrent
        else:
            current=graph.graph_inlink[current]
            if len(current) == 1:
                current = current[0]
            else:
                current = current[select(current, '%d-%d to select where to go' % (0, len(current)-1))]

            if current not in graph.graph_outlink:
                print '%s(%d) has no child\n' % (graph.cat__id_name[current], current)
                current = oldcurrent

browser(graph)
import code
code.interact(local=locals())
