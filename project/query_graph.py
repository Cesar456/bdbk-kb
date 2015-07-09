#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import re

from virtuoso import sparql

PREDICT_SEARCH_TERM = 'http://baike.baidu.com/graph#search_term'
PREDICT_BAIKE_TITLE = 'http://baike.baidu.com/graph#baike_title'
PREDICT_PREDICT_PREFIX = 'http://baike.baidu.com/predicts#'

sparql_connection = sparql.SparQL('http://localhost:8890/sparql/',
    'http://baike.baidu.com/')

def query_root(root_title):
    '''
    How do we present this graph to user:

    Current ne.
        Current ne (or current named entity) is the node (named entity)
        that we are navigating through. This will also be in part of page
        URL, for example, http://localhost/grapher#<something>.

        We continue search for nodes that is linked to current ne by its
        attribute values, that is, for example, when attribute of A has a
        link to ne B, then B is fetched and shown to user, but links in
        attributes of B will not be shown. After we switch current ne to
        B, the new links will pop up.

    Node types:
        There are two types of nodes: named entity, attributes. So there
        are also two types of links: ne-attribute, attribute-ne.
    '''

    # first of named_nodes will be current ne.
    named_nodes = []

    s,p,o = list(sparql_connection.query(
        predict=sparql.SparQLURI(PREDICT_BAIKE_TITLE),
        object=sparql.SparQLLiteral(root_title)))[0]

    assert isinstance(s, sparql.SparQLURI)

    named_nodes.append({
        'title': str(s),
        'attrs': []
        })

    regx = re.compile(r'\{\{link:([^|]*?)\|([^}]*?)\}\}')

    root = named_nodes[0]
    for s,p,o in sparql_connection.query(
        subject=sparql.SparQLURI(root['title'])):

        attr = {
            'predict': str(p),
            'value': re.sub(regx, lambda x:x.group(2), o)
        }

        root['attrs'].append(attr)

        # find out out links
        if isinstance(o, sparql.SparQLURI):
            subentities = [(o, '')]
        else:
            subentities = re.findall(regx, o)

        for out_link, _ in subentities:
            if out_link == root['title']:
                continue

            existing = False
            for subnes in named_nodes:
                if subnes['title'] == out_link:
                    existing = True
                    break
            if existing: break

            query = list(sparql_connection.query(
                subject=sparql.SparQLURI(out_link)))

            if len(query) > 0:
                named_nodes.append({'title': out_link, 'attrs': []})
                subnes = named_nodes[-1]

                for s,p,o in query:
                    attr = {
                        'predict': str(p),
                        'value': re.sub(regx, lambda x:x.group(2), o)
                    }
                    subnes['attrs'].append(attr)

    print json.dumps(named_nodes)

query_root(u'北京大学')
