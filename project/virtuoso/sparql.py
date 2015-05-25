#!/usr/bin/python
# -*- coding: utf8 -*-
from SPARQLWrapper import JSON, SPARQLWrapper


class SparQLVar(str):
    pass

class SparQLURI(SparQLVar):
    def sparql(self):
        return '<%s>' % super(SparQLURI, self).__str__()

class SparQLLiteral(SparQLVar):
    def sparql(self):
        return '"%s"' % super(SparQLLiteral, self).__str__()

def op_get_sparql():
    sparql = SPARQLWrapper("http://localhost:8890/sparql/")
    sparql.setMethod('POST')
    sparql.addParameter('default-graph-uri', 'http://localhost:8890/sparql')
    sparql.setReturnFormat(JSON)
    return sparql

def op_create_graph(sparql, graph_uri):
    '''
    Create a new named graph with uri. Returns None.

    Example:
        op_create_graph(sparql,
            SparQLURI("http://www.example.com/"))
    '''

    assert isinstance(graph_uri, SparQLVar)
    sparql.setQuery('''
        CREATE GRAPH %s
        ''' % graph_uri.sparql())

    results = sparql.query().convert()

def op_insert(sparql, subject, predict, object):
    '''
    Insert a tuple into graph. Returns None.

    Example:
        op_insert(sparql,
            SparQLURI("http://www.example.com/"),
            SparQLVar("ns:title"),
            SparQLVar("page"))
    '''
    assert isinstance(subject, SparQLVar)
    assert isinstance(predict, SparQLVar)
    assert isinstance(object, SparQLVar)

    sparql.setQuery('''
        INSERT DATA { %s %s %s }
        ''' % (subject.sparql(), predict.sparql(), object.sparql()))

    results = sparql.query().convert()

def op_delete(sparql, subject, predict, object):
    '''
    Delete a triple from graph. Returns None.

    Since virtuoso have no feedback when deleting
    triples, we really can't tell how many triples
    we have deleted.

    Example:
        op_delete(sparql, 
            SparQLURI("http://www.example.com/about"),
            SparQLURI("http://www.ns.com/title"),
            SparQLLiteral("about page"))
    '''
    assert isinstance(subject, SparQLVar)
    assert isinstance(predict, SparQLVar)
    assert isinstance(object, SparQLVar)

    sparql.setQuery('''
        DELETE DATA { %s %s %s }
        ''' % (subject.sparql(), predict.sparql(), object.sparql()))

    results = sparql.query().convert()

def op_query(sparql, subject=None, predict=None, object=None):
    '''
    Query the graph. Returns a generator of all
    matched queries.

    For simplcity, we preclude all datatypes in
    SPARQL except literals.

    Example:
        op_delete(sparql, 
            subject=SparQLURI("http://www.example.com/about"))
    '''

    bindings = []
    if subject is None:
        bindings.append({
            'constant': False,
            'binding': 's'
            })
    else:
        assert isinstance(subject, SparQLVar)
        bindings.append({
            'constant': True,
            'value': subject
            })
    if predict is None:
        bindings.append({
            'constant': False,
            'binding': 'p'
            })
    else:
        assert isinstance(predict, SparQLVar)
        bindings.append({
            'constant': True,
            'value': predict
            })
    if object is None:
        bindings.append({
            'constant': False,
            'binding': 'o'
            })
    else:
        assert isinstance(object, SparQLVar)
        bindings.append({
            'constant': True,
            'value': object
            })

    where_clause = []
    for i in bindings:
        if i['constant']:
            where_clause.append(i['value'].sparql())
        else:
            where_clause.append('?%s' % i['binding'])

    sparql.setQuery('''
        SELECT * WHERE { %s }
        ''' % ' '.join(where_clause))

    results = sparql.query().convert()
    for result in results['results']['bindings']:
        ret = []
        for i in bindings:
            if i['constant']:
                ret.append(i['value'])
            else:
                binding = i['binding']
                value_type = result[binding]['type']
                value = result[binding]['value']
                if value_type == 'uri':
                    ret.append(SparQLURI(value))
                else:
                    ret.append(SparQLLiteral(value.encode('utf8')))

        yield (ret[0], ret[1], ret[2])

sparql = op_get_sparql()
op_create_graph(sparql, SparQLURI("http://baike.baidu.com/"))
for s,p,o in op_query(sparql):
    print s, p, o
